# -*- coding: utf-8 -*-
from django.db.models import Count, Q

from contrib.utils import getLogger
from esocial.extractors.s1202 import S1202Extractor, S1202Factory
from esocial.models import S1207, Demonstrative1207, IdeEstabLot1207, IdePeriod1207
from rh.const import TYPE_BY_POSSESSION_BENEFICIARY
from rh.gfp.models import ContraCheque
from rh.models import BenefitMovement
from esocial.models import Configuration


log = getLogger(__name__)


class S1207Extractor(S1202Extractor):

    REGIME = (2, 3)

    def __init__(self, instance_outside, *args, **kwargs):
        super(S1207Extractor, self).__init__(instance_outside, *args, **kwargs)

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
        paychecks = ContraCheque.objects.filter(
            servidor__pessoa_fisica__cpf=registry_person,
            folha__periodo__mes=month,
            folha__periodo__ano=year,
            folha__status__in=(3, 4),
            pensioner__isnull=True,
        )

        return paychecks.filter(
            servidor__pk__in=cls._employees_for_paycheck(month, year, registry_person),
            servidor__type_by_possession__in=TYPE_BY_POSSESSION_BENEFICIARY,
        )

    def _set_registry_employee(self, employee):
        employee_benefit = Configuration.current_config().employee_benefit.filter()
        filter_benefit = employee_benefit.filter(
            pessoa_fisica__cpf=employee.pessoa_fisica.cpf
        )
        if filter_benefit.exists():
            return filter_benefit.first().matricula
        else:
            return employee.matricula

    def ide_benef_cpf_benef(self):
        return self.ide_trabalhador_cpf_trab()

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
                        "registry_employee": self._set_registry_employee(
                            paycheck.servidor
                        ),
                        "_class_": Demonstrative1207,
                        "oid": oid,
                        "rra": rra if rra else None,
                        "dm_dev_ide_dm_dev": oid,
                        "ide_evento_per_apur": self.ide_evento_per_apur(),
                        "info_pgto_dt_pgto": paycheck.folha.dt_pagamento,
                        "info_pgto_vr_liq": info_pgto_vr_liq,
                        "dm_dev_nr_beneficio": paycheck.benefit_number,
                        "info_per_apur_ide_estab_lot": ide_estab_lot,
                        "ide_period": ide_period,
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

    def ide_estab_lot(
        self,
        paycheck,
        reference_month=None,
        reference_year=None,
        ide_adc=None,
        per_apur=False,
        rra=False,
    ):
        if not reference_month:
            reference_month = self._period.mes
        if not reference_year:
            reference_year = self._period.ano

        createds = []
        if self.entries_by_reference_esocial(
            paycheck,
            reference_month,
            reference_year,
            ide_adc=ide_adc,
            per_apur=per_apur,
            rra=rra,
        ).exists():
            estab_buff = self.define_base_fields()
            estab_buff.update(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "competence_month": reference_month,
                    "competence_year": reference_year,
                    "registry_person": self.registry_person(),
                    "_class_": IdeEstabLot1207,
                    "oid": str(self.configuration.employer.pk),
                    "tp_insc": self.configuration.ide_employer_tp_insc,
                    "nr_insc": self.configuration.ide_employer_nr_insc,
                    "cod_lotacao": self.configuration.employer.pessoa_juridica.cnpj,
                    "qtd_dias_av": None,
                    "itens_remun": self.itens_remun(
                        paycheck,
                        reference_month,
                        reference_year,
                        ide_adc=ide_adc,
                        per_apur=per_apur,
                        rra=rra,
                    ),
                    "ide_adc": self.ide_adc_str(ide_adc),
                }
            )
            createds.append(estab_buff)
        return createds

    def ide_periodo(
        self, ide_adc, paycheck, per_apur=False, ide_period_cls=None, rra=False
    ):
        return super().ide_periodo(
            ide_adc, paycheck, per_apur=per_apur, ide_period_cls=IdePeriod1207, rra=rra
        )


class S1207Factory(S1202Factory):

    EXTRACTED_MODEL_CLASS = S1207
    EXTRACTOR = S1207Extractor

    @classmethod
    def _filter_specialized(cls):
        """Este método retorna um filter lookup que será aplicado em filter de _query_instance_outside.
        Neste caso retorna todos do regime definido no extrator e colaboradores eventuais do RPPS.

        Returns:
            (generator)"""
        return Q(
            servidor__socialsecurities__social_security_config__regime__in=cls.EXTRACTOR.REGIME,
            servidor__type_by_possession__in=TYPE_BY_POSSESSION_BENEFICIARY,
        )

    @classmethod
    def _exclude_specialized(cls):
        """Este método retorna um filter lookup que será aplicado em exclude de _query_instance_outside.
        Neste caso exclue os beneficiários.

        Returns:
            (generator)"""
        return None
