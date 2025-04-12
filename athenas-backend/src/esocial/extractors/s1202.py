# -*- coding: utf-8 -*-
from django.db.models import Count, Q

from contrib.utils import getLogger
from esocial.extractors.s1200 import S1200Extractor, S1200Factory
from esocial.extractors.s2200 import employee_cod_categ
from esocial.models import S1202, Demonstrative1202, get_current_config
from rh.const import TYPE_BY_POSSESSION_BENEFICIARY
from rh.models import SocialSecurityEmployee

log = getLogger(__name__)


class S1202Extractor(S1200Extractor):

    REGIME = (2, 3)

    def __init__(self, instance_outside, *args, **kwargs):
        super(S1202Extractor, self).__init__(instance_outside, *args, **kwargs)

    @classmethod
    def paychecks(cls, month, year, registry_person=None):
        """Este método retorna os contracheques possíveis para per_apur e per_ant.

        Args:
            month (int):
            year (int):
            registry_person (str): cpf da pessoa física

        Returns:
            values_list('pk')
        """
        return (
            super()
            .paychecks(month, year, registry_person=registry_person)
            .exclude(Q(servidor__type_by_possession__in=TYPE_BY_POSSESSION_BENEFICIARY))
        )

    @classmethod
    def entries_by_reference_esocial(
        cls, paycheck, month, year, ide_adc=None, per_apur=False, rra=False
    ):
        """Este método gera o queryset para o período de apuração a partir de um contracheque. Filtra o FolhaEvento por monht, year e per_apur.

        Returns:
            FolhaEvento.queryset:"""
        months = [month]
        if month == 12:
            months.append(13)

        q_reference = Q(reference_month__in=months, reference_year=year)

        if per_apur:
            q_reference = Q(reference_month__gte=month, reference_year=year) | Q(
                reference_year__gt=year
            )
        query = (
            paycheck.lancamentos.filter(
                Q(status__in=("CT", "CE", "BS"), folha__status__in=(3, 4)) & q_reference
            )
            .filter(contracheque__pensioner__isnull=True)
            .exclude(valor=0)
        )

        if rra:
            query = query.filter(rra_employee__pk=rra)
        else:
            query = query.filter(rra_employee__isnull=True)

        return query

    @classmethod
    def entries_by_reference_per_ant_esocial(cls, paycheck, month, year, rra=False):
        """Este método gera o queryset para o período de apuração anterior a partir de um contracheque. Filtra o FolhaEvento por month e year.

        Returns:
            FolhaEvento.queryset:"""
        query = (
            paycheck.lancamentos.filter(
                status__in=("CT", "CE", "BS"),
                folha__status__in=(3, 4),
                contracheque__pensioner__isnull=True,
            )
            .filter(
                (Q(reference_month__lt=month) & Q(reference_year=year))
                | Q(reference_year__lt=year)
            )
            .exclude(valor=0)
        )

        if rra:
            query = query.filter(rra_employee__pk=rra)
        else:
            query = query.filter(rra_employee__isnull=True)

        return query

    def dm_dev(self):
        self._dm_dev_infos = {}
        self._dm_dev = []

        def gen_paycheck(paycheck, rra=False):
            oid = self.oid_paycheck(paycheck, rra=rra)

            ide_period = self.ide_periodo(None, paycheck, per_apur=False, rra=rra)
            ide_estab_lot = self.ide_estab_lot(paycheck, per_apur=True, rra=rra)

            if ide_period or ide_estab_lot:
                dm_dev_info = self._dm_dev_infos.get(oid, {})

                dm_buff = self.define_base_fields()
                dm_buff = self.define_rra_fields(
                    dm_dev=dm_buff, dm_dev_info=dm_dev_info, rra=rra
                )

                info_pgto_vr_liq = dm_dev_info.get("info_pgto_vr_liq", 0)

                dm_buff.update(
                    {
                        "start_validity": self.start_validity(),
                        "end_validity": self.end_validity(),
                        "competence_month": self._period.mes,
                        "competence_year": self._period.ano,
                        "registry_person": self.registry_person(),
                        "registry_employee": paycheck.servidor.matricula,
                        "_class_": Demonstrative1202,
                        "oid": oid,
                        "rra": rra if rra else None,
                        "dm_dev_ide_dm_dev": oid,
                        "ide_evento_per_apur": self.ide_evento_per_apur(),
                        "info_pgto_dt_pgto": paycheck.folha.dt_pagamento,
                        "info_pgto_vr_liq": info_pgto_vr_liq,
                        "dm_dev_cod_categ": employee_cod_categ(
                            paycheck.servidor, info="RPPS"
                        ),
                        "info_per_apur_ide_estab_lot": ide_estab_lot,
                        "ide_period": ide_period,
                        "remun_org_suc": "N" if ide_period else None,
                    }
                )
                self._dm_dev.append(dm_buff)

        paychecks = self.paychecks(
            self._period.mes, self._period.ano, self._instance_outside.cpf
        )

        """Contracheques sem RRA."""
        for paycheck in (
            paychecks.filter(lancamentos__rra_employee__isnull=True)
            .distinct()
            .order_by("servidor")
        ):
            gen_paycheck(paycheck)

        """Contracheques com RRA."""
        paychecks_rra = (
            paychecks.filter(lancamentos__rra_employee__isnull=False)
            .values("lancamentos__rra_employee")
            .order_by("lancamentos__rra_employee")
            .annotate(count_rra_employee=Count("lancamentos__rra_employee"))
        )
        for paycheck_rra in paychecks_rra.distinct().order_by("servidor"):
            for paycheck in (
                paychecks.filter(
                    lancamentos__rra_employee=paycheck_rra.get(
                        "lancamentos__rra_employee"
                    )
                )
                .distinct()
                .order_by("servidor")
            ):
                gen_paycheck(
                    paycheck, rra=paycheck_rra.get("lancamentos__rra_employee")
                )

        return self._dm_dev

    def ide_periodo(
        self, ide_adc, paycheck, per_apur=False, ide_period_cls=None, rra=False
    ):
        createds = []
        if not self._ide_period_query_per_ant(paycheck, rra=rra).exists():
            return createds
        return super().ide_periodo(
            ide_adc, paycheck, per_apur=per_apur, ide_period_cls=ide_period_cls, rra=rra
        )


class S1202Factory(S1200Factory):

    EXTRACTED_MODEL_CLASS = S1202
    EXTRACTOR = S1202Extractor

    @classmethod
    def _filter_specialized(cls):
        """Este método retorna um filter lookup que será aplicado em filter de _query_instance_outside.
        Neste caso retorna todos do regime definido no extrator ou colaboradores eventuais do RPPS.

        Returns:
            (generator)"""
        # query_occasional_collaborator = (pk for pk in SocialSecurityEmployee.objects.filter(
        #     employee__type_by_possession='COE').exclude(
        #     social_security_config__regime=1).values_list('employee__pessoa_fisica__pk', flat=True))

        return Q(
            servidor__socialsecurities__social_security_config__regime__in=cls.EXTRACTOR.REGIME
        )

    @classmethod
    def _exclude_specialized(cls):
        """Este método retorna um filter lookup que será aplicado em exclude de _query_instance_outside.
        Neste caso exclue os beneficiários.

        Returns:
            (generator)"""
        return Q(servidor__type_by_possession="COE")
