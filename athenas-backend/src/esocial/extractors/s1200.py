# -*- coding: utf-8 -*-
from django.db.models import Count, Q
from django.template.defaultfilters import striptags

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from esocial.const import MAP_REASON_DIFFERENCE_IADC, NOTHING_TODO
from esocial.extractors.base import Extractor, Factory
from esocial.extractors.s1010 import S1010Extractor
from esocial.extractors.s2200 import employee_cod_categ
from esocial.models import (
    S1200,
    Demonstrative,
    DemonstrativeItem,
    IdeAdc,
    IdeEstabLot,
    IdePeriod,
    ProcJudTrab,
    RemunOutrEmpr,
    RemunPeriod,
    get_current_config,
)
from rh.gfp.models import (
    ContraCheque,
    Evento,
    FolhaEvento,
    RRAEmployee,
    RemunerationRelationship,
)
from rh.models import PessoaFisica, ProcessSuspension, SocialSecurityEmployee
from standard.models import Choice
from esocial.const import DATE_V12
import decimal


log = getLogger(__name__)


class ExtractorPayroll(Extractor):

    def __init__(self, instance_outside, *args, **kwargs):
        self._dm_dev = []
        self._info_irrf_cr = []
        self._info_dep = []
        self.prev_complem = None
        super().__init__(instance_outside, *args, **kwargs)

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""
        references = self._references()
        return self._start_validity, self._end_validity, references

    def _references(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return self._references_strong()

    def _references_strong(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return [self._instance_outside]

    def pos_validate(self):
        if not self._event and not self._dm_dev:
            return NOTHING_TODO
        return super().pos_validate()

    @classmethod
    def _ide_evento_per_apur(cls, month, year):
        """
            Informar o mês/ano (formato AAAA-MM) de referência das informações, se
            {indApuracao} for igual a [1], ou apenas o ano (formato AAAA), se
            {indApuracao} for igual a [2]
            Validação: Deve ser um mês/ano ou ano válido, igual ou posterior a
            implementação do eSocial.

        Args:
            period(Periodo):

        Returns
            per_apur(str): formato AAAA-MM ou AAAA
        """
        if month == 13:
            return f"{year}"
        return "{}-{:02d}".format(year, month)

    def ide_evento_per_apur(self):
        """
        Informar o mês/ano (formato AAAA-MM) de referência das informações, se
        {indApuracao} for igual a [1], ou apenas o ano (formato AAAA), se
        {indApuracao} for igual a [2]
        Validação: Deve ser um mês/ano ou ano válido, igual ou posterior a
        implementação do eSocial.
        """
        return self._ide_evento_per_apur(self._period.mes, self._period.ano)

    def ide_evento_ind_apuracao(self):
        """
        Indicativo de período de apuração:
        1 - Mensal;
        2 - Anual (13° salário).
        Valores Válidos: 1, 2
        """
        if self._period.mes == 13:
            return 2
        return 1

    def competence_month(self):
        return self._period.mes

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
            folha__status__in=(3, 4),
            pensioner__isnull=True,
            folha__periodo__mes=month,
            folha__periodo__ano=year,
        )

        if registry_person:
            paychecks = paychecks.filter(servidor__pessoa_fisica__cpf=registry_person)

            config = get_current_config()
            paychecks = paychecks.exclude(
                servidor__matricula__in=(
                    registry
                    for registry in config.employee_exclude.filter(
                        pessoa_fisica__cpf=registry_person
                    ).values_list("matricula", flat=True)
                )
            )

            if config.employee_filter.filter(
                pessoa_fisica__cpf=registry_person
            ).exists():
                paychecks = paychecks.filter(
                    servidor__matricula__in=(
                        registry
                        for registry in config.employee_filter.filter(
                            pessoa_fisica__cpf=registry_person
                        ).values_list("matricula", flat=True)
                    )
                )

        return paychecks

    @classmethod
    def all_entries_by_reference_esocial(cls, month, year, registry_person=None):
        """Este método retorna todos FolhaEvento por mês(month) e ano(year).

        Returns:
            FolhaEvento.queryset:"""
        paychecks = cls.paychecks(month, year, registry_person=registry_person)

        return FolhaEvento.objects.filter(
            pk__in=(
                pk
                for pk in paychecks.filter(
                    Q(
                        lancamentos__status__in=("CT", "CE", "BS"),
                        folha__status__in=(3, 4),
                    )
                )
                .filter(pensioner__isnull=True)
                .values_list("lancamentos__pk", flat=True)
            )
        ).exclude(valor=0)

    @classmethod
    def entries_not_in_demonstrative_item(cls, month, year):
        """Este método retorna todos FolhaEvento por mês(month) e ano(year) que não possuem event_esocial.

        Returns:
            FolhaEvento.queryset:"""
        per_apur = cls._ide_evento_per_apur(month, year)

        oids_dm_items = (
            oid
            for oid in DemonstrativeItem.objects.demonstrative_item_all(
                per_apur=per_apur
            )
            .filter(is_invalid_cache=False, has_exclusion_cache=False)
            .values_list("oid", flat=True)
        )
        return (
            cls.all_entries_by_reference_esocial(month, year)
            .filter(event_esocial__isnull=True)
            .exclude(pk__in=oids_dm_items)
        )

    def define_base_fields(self):
        """Este método define os campos básicos para Event que não possuírem extrator.

        Returns:
            dict"""
        return {
            "ide_empregador_tp_insc": self.ide_empregador_tp_insc(),
            "ide_empregador_nr_insc": self.ide_empregador_nr_insc(),
            "ide_evento_per_apur": self.ide_evento_per_apur(),
            "ide_evento_tp_amb": self.ide_evento_tp_amb(),
            "ide_evento_proc_emi": self.ide_evento_proc_emi(),
            "ide_evento_ver_proc": self.ide_evento_ver_proc(),
        }

    @classmethod
    def define_rra_fields(cls, dm_dev={}, dm_dev_info={}, rra=False):
        """Este método define os campos básicos do demonstrativo com RRA.

        Returns:
            dict"""
        rra_fld = None
        dm_dev_ind_rra = None
        info_rra_tp_proc_rra = None
        info_rra_nr_proc_rra = None
        info_rra_desc_rra = None
        info_rra_qtd_meses_rra = None
        desp_proc_jud_vlr_desp_custas = None
        desp_proc_jud_vlr_desp_advogados = None

        if rra:
            rra_fld = str(rra)
            dm_dev_ind_rra = "S"
            rra_employee = RRAEmployee.objects.filter(pk=rra).last()
            info_rra_tp_proc_rra = rra_employee.rra.process_type
            if rra_employee.rra.process_type != 1:
                info_rra_nr_proc_rra = (
                    rra_employee.rra.process.replace(".", "")
                    .replace("/", "")
                    .replace("-", "")
                )
            info_rra_desc_rra = rra_employee.rra.title

            desp_proc_jud_vlr_desp_custas = None
            desp_proc_jud_vlr_desp_advogados = None

            info_rra_qtd_meses_rra = rra_employee.months
            rra_prazo = dm_dev_info.get("rra_prazo", 1)
            rra_installments_paid = dm_dev_info.get("rra_installments_paid", 1)
            if rra_prazo:
                info_rra_qtd_meses_rra = info_rra_qtd_meses_rra / rra_prazo
            if rra_installments_paid:
                info_rra_qtd_meses_rra = info_rra_qtd_meses_rra * rra_installments_paid

        dm_dev.update(
            {
                "rra": rra_fld,
                "dm_dev_ind_rra": dm_dev_ind_rra,
                "info_rra_tp_proc_rra": info_rra_tp_proc_rra,
                "info_rra_nr_proc_rra": info_rra_nr_proc_rra,
                "info_rra_desc_rra": info_rra_desc_rra,
                "info_rra_qtd_meses_rra": info_rra_qtd_meses_rra,
                "desp_proc_jud_vlr_desp_custas": desp_proc_jud_vlr_desp_custas,
                "desp_proc_jud_vlr_desp_advogados": desp_proc_jud_vlr_desp_advogados,
            }
        )
        return dm_dev


class S1200Extractor(ExtractorPayroll):

    REGIME = (1,)

    def __init__(self, instance_outside, *args, **kwargs):
        super(S1200Extractor, self).__init__(instance_outside, *args, **kwargs)

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

        config = get_current_config()
        paychecks = paychecks.exclude(
            servidor__matricula__in=(
                registry
                for registry in config.employee_exclude.filter(
                    pessoa_fisica__cpf=registry_person
                ).values_list("matricula", flat=True)
            )
        )

        if config.employee_filter.filter(pessoa_fisica__cpf=registry_person).exists():
            paychecks = paychecks.filter(
                servidor__matricula__in=(
                    registry
                    for registry in config.employee_filter.filter(
                        pessoa_fisica__cpf=registry_person
                    ).values_list("matricula", flat=True)
                )
            )

        return paychecks.filter(
            Q(
                servidor__pk__in=cls._employees_for_paycheck(
                    month, year, registry_person
                )
            )
            | Q(servidor__type_by_possession="COE")
        )

    @classmethod
    def _employees_for_paycheck(cls, month, year, registry_person):
        """Este método retorna os servidores possíveis de contracheque. Analisa se existe SocialSecurityEmployee no período informado.

        Args:
            month (int):
            year (int):
            registry_person (str): cpf da pessoa física

        Returns:
            values_list('pk')
        """
        sses = SocialSecurityEmployee.objects.filter(
            employee__pessoa_fisica__cpf=registry_person,
            social_security_config__regime__in=cls.REGIME,
        )
        dr = NewDateRange.from_month(year, 12 if month == 13 else month)
        sse = sses.currents_in(range=dr)
        if not sse.exists():
            sse = sses.filter(
                Q(employee__termination_date__isnull=False)
                & Q(employee__termination_date__lt=dr.first)
            )
        return (employee for employee in sse.values_list("employee", flat=True))

    @classmethod
    def entries_by_reference_esocial(
        cls, paycheck, month, year, ide_adc=None, per_apur=False, rra=False
    ):
        """Este método gera o queryset para o período de apuração a partir de um contracheque. Filtra o FolhaEvento por month, year e per_apur.

        Returns:
            FolhaEvento.queryset:"""
        if not per_apur:
            """PERANT"""
            reason_difference = (2,)
            if ide_adc and ide_adc[1] == "B":
                reason_difference = (3, 4)

            months = [month]
            if month == 12:
                months.append(13)

            q_reference = Q(
                reference_month__in=months,
                reference_year=year,
                reason_difference__in=reason_difference,
            )

        else:
            """PERAPUR"""
            q_per_apur = Q(
                contracheque__folha__periodo__mes=month,
                contracheque__folha__periodo__ano=year,
            ) & (
                Q(reference_month__gte=month, reference_year=year)
                | Q(reference_year__gt=year)
            )
            q_per_apur_ahead = ~Q(
                contracheque__folha__periodo__mes=month,
                contracheque__folha__periodo__ano=year,
            ) & (
                Q(
                    reference_month=month,
                    reference_year=year,
                    reason_difference__in=(1, 4),
                )
            )
            q_reference = q_per_apur | q_per_apur_ahead

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
                reason_difference__in=(2, 3, 4),
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

    def pre_validate(self):
        if not self.paychecks(
            self._period.mes, self._period.ano, self._instance_outside.cpf
        ).exists():
            return NOTHING_TODO
        return super().pre_validate()

    def oid(self):
        return self._get_oid(
            self._instance_outside, month=self._period.mes, year=self._period.ano
        )

    @classmethod
    def _get_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        month = kwargs.get("month", "*")
        year = kwargs.get("year", "*")
        return f"{year}{month:02d}{instance_outside.cpf}"

    def description(self):
        type_by_possession = (
            self.paychecks(
                self._period.mes, self._period.ano, self._instance_outside.cpf
            )
            .distinct()
            .values_list("servidor__type_by_possession", flat=True)
        )
        description = ""
        description += " ".join(set(type_by_possession))
        return f"{description} {self._instance_outside.cpf}: {self._instance_outside} | {self.competence_month()}/{self.competence_year()}"

    def registry_person(self):
        return self._instance_outside.cpf

    def registry_employee(self):
        return None

    def ide_trabalhador_cpf_trab(self):
        return self._instance_outside.cpf

    def ide_trabalhador_nis_trab(self):
        nis = self._instance_outside.nis
        pis_pasep = self._instance_outside.pis_pasep
        number = ""
        if nis:
            number = nis.numero
        if pis_pasep:
            number = pis_pasep.numero
        return number[:11]

    def info_mv_ind_mv(self):
        paychecks = ExtractorPayroll.paychecks(
            self._period.mes if self._period.mes != 13 else 12,
            self._period.ano,
            registry_person=self.registry_person(),
        )
        entries = FolhaEvento.objects.filter(
            pk__in=(
                pk
                for pk in paychecks.filter(
                    Q(
                        lancamentos__status__in=("CT", "CE", "BS"),
                        folha__status__in=(3, 4),
                    )
                )
                .filter(pensioner__isnull=True)
                .values_list("lancamentos__pk", flat=True)
            )
        ).filter(json_calc_vars__icontains="indMV")

        ind_mv = [entry.vars.get("indMV") for entry in entries]
        if ind_mv:
            return max(ind_mv)

        return None

    def remun_outr_empr(self):
        createds = []
        query = RemunerationRelationship.objects.filter(
            employee__pessoa_fisica=self._instance_outside
        ).currents_between(self._period.start_date, self._period.end_date)
        for remuneration_relationship in query:
            remun_outr_empr_tp_insc = ""
            remun_outr_empr_nr_insc = ""

            buff = self.define_base_fields()

            natural_person = getattr(
                remuneration_relationship.person_payer, "pessoafisica", None
            )
            legal_person = getattr(
                remuneration_relationship.person_payer, "pessoajuridica", None
            )
            if natural_person:
                remun_outr_empr_tp_insc = 2
                remun_outr_empr_nr_insc = natural_person.cpf
            elif legal_person:
                remun_outr_empr_tp_insc = 1
                remun_outr_empr_nr_insc = legal_person.cnpj

            buff.update(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "competence_month": self._period.mes,
                    "competence_year": self._period.ano,
                    "registry_person": self.registry_person(),
                    "_class_": RemunOutrEmpr,
                    "oid": str(remuneration_relationship.pk),
                    "remun_outr_empr_tp_insc": remun_outr_empr_tp_insc,
                    "remun_outr_empr_nr_insc": remun_outr_empr_nr_insc,
                    "remun_outr_empr_cod_categ": remuneration_relationship.category_esocial,
                    "remun_outr_empr_vlr_remun_oe": remuneration_relationship.remuneration,
                }
            )
            createds.append(buff)
        return createds

    def remun_outr_empr_tp_insc(self):
        return None

    def remun_outr_empr_nr_insc(self):
        return None

    def remun_outr_empr_cod_categ(self):
        return None

    def remun_outr_empr_vlr_remun_oe(self):
        return None

    def info_complem_nm_trab(self):
        return None

    def info_complem_dt_nascto(self):
        return None

    def proc_jud_trab(self):
        suspensions = []
        query_suspensions = (
            ProcessSuspension.objects.filter(
                process__employees__pessoa_fisica__cpf=self._instance_outside.cpf
            )
            .currents_in(drange=NewDateRange(self._start_validity, self._end_validity))
            .filter(process__matter_process=1, scope_decision__in=(1, 2))
        )  # tributária  # abrange contribuições sociais
        for suspension in query_suspensions:
            susp_buff = self.define_base_fields()
            susp_buff.update(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "competence_month": self._period.mes,
                    "competence_year": self._period.ano,
                    "registry_person": self.registry_person(),
                    "_class_": ProcJudTrab,
                    "oid": str(suspension.process.pk),
                    "proc_jud_trab_nr_proc_jud": suspension.process.number_process,
                    "proc_jud_trab_cod_susp": suspension.id,
                    "proc_jud_trab_tp_trib": suspension.process.type_process,
                }
            )
            suspensions.append(susp_buff)
            self.set_dependency(
                oid=suspension.process.number_process,
                filter_query_instance=Q(
                    number_process=suspension.process.number_process
                ),
                acronyms=("s1070",),
            )
        return suspensions

    @classmethod
    def oid_paycheck(cls, paycheck, rra=False):
        oid = f"{paycheck.pk}"
        # return oid
        return f"{oid}{rra}" if rra else oid

    def dm_dev(self):
        self._dm_dev_infos = {}
        self._dm_dev = []

        def gen_paycheck(paycheck, rra=False):
            oid = self.oid_paycheck(paycheck, rra=rra)

            per_apur = self.ide_estab_lot(paycheck, per_apur=True, rra=rra)
            per_ant = self.ide_adc(paycheck, rra=rra)

            if per_apur or per_ant:
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
                        "_class_": Demonstrative,
                        "oid": oid,
                        "dm_dev_ide_dm_dev": oid,
                        "rra": rra if rra else None,
                        "ide_evento_per_apur": self.ide_evento_per_apur(),
                        "info_pgto_dt_pgto": paycheck.folha.dt_pagamento,
                        "info_pgto_vr_liq": info_pgto_vr_liq,
                        "dm_dev_cod_categ": employee_cod_categ(
                            paycheck.servidor, info="RGPS"
                        ),
                        "info_per_apur_ide_estab_lot": per_apur,
                        "ide_adc": per_ant,
                        "info_compl_cont_cod_cbo": self.info_compl_cont_cod_cbo(
                            paycheck
                        ),
                        "info_compl_cont_nat_atividade": self.info_compl_cont_nat_atividade(),
                        "info_compl_cont_qtd_dias_trab": None,
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

    def info_compl_cont_cod_cbo(self, paycheck):
        # FIXME: DEFINIR DE ONDE O CBO VIRÁ
        return "411010" if paycheck.servidor.is_occasional_collaborator else None

    def info_compl_cont_cod_cbo(self, paycheck):
        # FIXME: DEFINIR DE ONDE O CBO VIRÁ
        return "411010" if paycheck.servidor.is_occasional_collaborator else None

    def info_compl_cont_nat_atividade(self):
        value = None
        if self.configuration.ide_employer_tp_insc in (6, 7, 8):
            value = 1
        return value

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

        entries = self.entries_by_reference_esocial(
            paycheck,
            reference_month,
            reference_year,
            ide_adc=ide_adc,
            per_apur=per_apur,
            rra=rra,
        )

        createds = []
        if entries.exists():
            estab_buff = self.define_base_fields()
            estab_buff.update(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "competence_month": reference_month,
                    "competence_year": reference_year,
                    "registry_person": self.registry_person(),
                    "_class_": IdeEstabLot,
                    "oid": str(self.configuration.employer.pk),
                    "tp_insc": self.configuration.ide_employer_tp_insc,
                    "nr_insc": self.configuration.ide_employer_nr_insc,
                    "cod_lotacao": self.configuration.employer.pessoa_juridica.cnpj,
                    "qtd_dias_av": None,
                    "remun_period": self.remun_period(
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

    def ide_adc(self, paycheck, rra=False):
        period_query_per_ant = self._ide_period_query_per_ant(paycheck, rra=rra)

        ide_adcs = {}

        def list_ide_adcs():
            reason = Choice.objects.filter(app_label="gfp", name="DIFFERENCE_TYPE")
            for entry in (
                period_query_per_ant.values("reason_difference")
                .order_by("reason_difference")
                .annotate(reason_difference_count=Count("reason_difference"))
            ):

                # 2: 'A',  # Acordo Coletivo de Trabalho
                # 1: 'B',  # Diferenças realacionadas diversas "IN RFB nº 2.107/22"
                # 3: 'B',  # Legislação federal, estadual, municipal ou distrital
                # 4: 'B',  # Diferenças realacionadas diversas "IN RFB nº 2.107/22"

                ide_adc_dt_ac_conv = self.start_validity()
                ide_adc_tp_ac_conv = MAP_REASON_DIFFERENCE_IADC.get(
                    entry.get("reason_difference")
                )
                ide_adc_dsc = reason.get(
                    value=entry.get("reason_difference")
                ).description

                # FIXME: MODIFICAR 1 PARA 4 NO CASO DE PAS, POIS PAS É DE DIFERENÇA ANTERIOR

                if entry.get("reason_difference") in (3, 4):
                    ide_adc_dsc = "IN RFB nº 2.107/22"

                ide_adcs.update(
                    {
                        (ide_adc_dt_ac_conv, ide_adc_tp_ac_conv): {
                            # FIXME: DEFINIR ORIGEM DE ide_adc_dt_ac_conv, POIS NÃO PODE SER O start_validity
                            "ide_adc_dt_ac_conv": ide_adc_dt_ac_conv,
                            "ide_adc_tp_ac_conv": ide_adc_tp_ac_conv,
                            "ide_adc_dsc": striptags(ide_adc_dsc),
                            "ide_adc_remun_suc": "N",
                        }
                    }
                )

        list_ide_adcs()

        createds = []
        if period_query_per_ant.exists():
            for adc in ide_adcs:
                ide_adc = ide_adcs[adc]
                adc_buff = self.define_base_fields()
                oid = f"{adc[0].strftime('%Y%m%d')}{adc[1]}"
                adc_buff.update(
                    {
                        "start_validity": self.start_validity(),
                        "end_validity": self.end_validity(),
                        "competence_month": self._period.mes,
                        "competence_year": self._period.ano,
                        "registry_person": self.registry_person(),
                        "_class_": IdeAdc,
                        "oid": oid,
                        "ide_adc_dt_ac_conv": ide_adc.get("ide_adc_dt_ac_conv"),
                        "ide_adc_tp_ac_conv": ide_adc.get("ide_adc_tp_ac_conv"),
                        "ide_adc_dsc": ide_adc.get("ide_adc_dsc"),
                        "ide_adc_remun_suc": ide_adc.get("ide_adc_remun_suc"),
                        "ide_period": self.ide_periodo(adc, paycheck, rra=rra),
                    }
                )
                createds.append(adc_buff)
        return createds

    def remun_period(
        self,
        paycheck,
        reference_month,
        reference_year,
        ide_adc=None,
        per_apur=False,
        rra=False,
    ):
        registry = f"{paycheck.servidor.matricula}"
        if paycheck.servidor.is_occasional_collaborator:
            registry = None

        remun_buff = self.define_base_fields()
        remun_buff.update(
            {
                "start_validity": self.start_validity(),
                "end_validity": self.end_validity(),
                "competence_month": reference_month,
                "competence_year": reference_year,
                "registry_person": self.registry_person(),
                "_class_": RemunPeriod,
                "oid": str(paycheck.pk),
                "matricula": registry,
                "ind_simples": None,
                "itens_remun": self.itens_remun(
                    paycheck,
                    reference_month,
                    reference_year,
                    ide_adc=ide_adc,
                    per_apur=per_apur,
                    rra=rra,
                ),
                "grau_exp": self.grau_exp(paycheck.servidor),
            }
        )
        return [remun_buff]

    def grau_exp(self, employee):
        """
        O (se codCateg = [1XX, 2XX, 3XX, 731, 734, 738] ou se codCateg = 4XX] com {categOrig} em S-
            2300 = [1XX, 2XX, 3XX, 731, 734, 738]);
        N (nos demais casos)"""
        cod_categ = employee_cod_categ(employee, info="RGPS")
        if str(cod_categ)[:1] in ("1", "2", "3", "4") or cod_categ in (731, 734, 738):
            return 1
        return None

    def itens_remun(
        self,
        paycheck,
        reference_month,
        reference_year,
        ide_adc=None,
        per_apur=False,
        rra=False,
    ):
        """Este método gera os itens de remunerações(DemonstrativeItem) por contracheque.

        Args:
            paycheck (ContraCheque): _description_
            reference_month (int): _description_
            reference_year (int): _description_
            ide_adc (inte, optional): _description_. Defaults to None.
            per_apur (bool, optional): _description_. Defaults to False.

        Returns:
            list: lista de DemonstrativeItem
        """

        def adjust_paycheck(entry, total_adjust, vr_rubr):
            """Este método verifica se existe alguma configuração de ajuste. Ou seja, algum evento do mesmo genre_event, de entry, com
            configuração de esocial_cp__code '00' ou esocial_cprp__code '00' ou esocial_irrf__code '9'.
                Aplica os valores encontrados a total_adjust e o vr_rubr de entry.

            Args:
                entry (FolhaEvento): _description_
                total_adjust (Decimal): _description_
                vr_rubr (Decimal): _description_

            Returns:
                Decimal, Decimal: total_adjust, vr_rubr
            """
            if entry.evento.specie_event.specie_number == "00":
                rgps = entry.evento.tags.filter(label="rgps").exists()
                rpps = entry.evento.tags.filter(label="rpps").exists()
                irrf = entry.evento.tags.filter(label="irrf").exists()
                if rgps or rpps or irrf:
                    entries_adjust = (
                        FolhaEvento.objects.filter(
                            servidor=entry.servidor,
                            reference_year=reference_year,
                            reference_month=reference_month,
                            evento__genre_event=entry.evento.genre_event,
                        )
                        .filter(
                            Q(status__in=("CT", "CE", "BS"), folha__status__in=(3, 4))
                        )
                        .filter(contracheque__pensioner__isnull=True)
                        .exclude(valor=0)
                    )

                    drange = entry.folha.date_range
                    start_date = drange.first
                    end_date = drange.last
                    for entry_adjust in entries_adjust:
                        q_entry_adjust = entry_adjust.evento.configs.validity_in(
                            start_date, end_date
                        )
                        if (
                            rgps
                            and q_entry_adjust.filter(esocial_cp__code="00").exists()
                        ):
                            vr_rubr -= entry_adjust.value
                            total_adjust += entry_adjust.value
                        elif (
                            rpps
                            and q_entry_adjust.filter(esocial_cprp__code="00").exists()
                        ):
                            vr_rubr -= entry_adjust.value
                            total_adjust += entry_adjust.value
                        elif (
                            irrf
                            and q_entry_adjust.filter(esocial_irrf__code="9").exists()
                        ):
                            vr_rubr -= entry_adjust.value
                            total_adjust += entry_adjust.value
            return total_adjust, vr_rubr

        def generate_adjust_remun(itens, total_adjust):
            """Este método adiciona um DemonstrativeItem de acordo com o valor encontrado em total_adjust:
                quando maior que 0, o tipo do Evento será 'P'; de outra forma será 'D'.
                O vr_rubr será o total_adjust.

            Args:
                itens (list): list de itens_remun
                total_adjust (Decimal): _description_
            """
            total_adjust = round(abs(total_adjust), 2)
            if total_adjust:
                # Buscando verba de ajuste
                event_type = "P" if total_adjust > 0 else "D"
                adjustment_event = Evento.objects.filter(
                    tags__label="ajusteesocial", tipo=event_type
                ).last()
                tab_rubr = S1010Extractor.get_tab_rubr(
                    adjustment_event.numero,
                    start_validity=self._start_validity,
                    end_validity=self._end_validity,
                    employee=paycheck.servidor,
                )
                oid_rubr = S1010Extractor._get_oid(
                    adjustment_event,
                    start_validity=self._start_validity,
                    end_validity=self._end_validity,
                    organizer=tab_rubr,
                )

                item_buff = self.define_base_fields()
                item_buff.update(
                    {
                        "start_validity": self.start_validity(),
                        "end_validity": self.end_validity(),
                        "competence_month": self._period.mes,
                        "competence_year": self._period.ano,
                        "registry_person": self.registry_person(),
                        "_class_": DemonstrativeItem,
                        "oid": f"A{paycheck.pk}",
                        "cod_rubr": adjustment_event.numero,
                        "oid_rubr": oid_rubr,
                        "ide_tab_rubr": tab_rubr,
                        "qtd_rubr": None,
                        "fator_rubr": None,
                        "vr_rubr": total_adjust,
                        # FIXME: DEFINIR COM DGPFP ind_apur_ir #2409
                        # TODO: AVALIAR MOS ESOCIAL NO ITEM 10
                        "ind_apur_ir": 0,
                    }
                )
                itens.append(item_buff)

                msg = f"Ajuste inserido no desmontrativo: {adjustment_event} - valor: {total_adjust}"
                msg += f" - {PessoaFisica.objects.get(cpf=self.registry_person())} - {self.registry_person()}"
                msg += f" | {self._period.mes}/{self._period.ano}"
                self.task_info(msg=msg, type_of=2)

        entries = self.entries_by_reference_esocial(
            paycheck,
            reference_month,
            reference_year,
            ide_adc=ide_adc,
            per_apur=per_apur,
            rra=rra,
        )

        dm_dev_info = self._dm_dev_infos.get(self.oid_paycheck(paycheck, rra=rra), {})
        total_net = dm_dev_info.get("info_pgto_vr_liq", 0)
        rra_prazo = dm_dev_info.get("rra_prazo", 1)
        rra_installments_paid = dm_dev_info.get("rra_installments_paid", 1)

        total_adjust = 0
        createds = []
        for entry in entries:
            vr_rubr = entry.valor
            total_net += entry.value
            if rra:
                if rra_prazo < entry.prazo:
                    rra_prazo = entry.prazo
                if rra_prazo < entry.installments_paid:
                    rra_installments_paid = entry.installments_paid

            tab_rubr = S1010Extractor.get_tab_rubr(
                entry.evento.numero,
                start_validity=self._start_validity,
                end_validity=self._end_validity,
                employee=paycheck.servidor,
            )
            oid_rubr = S1010Extractor._get_oid(
                entry.evento,
                start_validity=self._start_validity,
                end_validity=self._end_validity,
                organizer=tab_rubr,
            )

            """Calcula e ajusta vr_rubr."""
            total_adjust, vr_rubr = adjust_paycheck(entry, total_adjust, vr_rubr)

            item_buff = self.define_base_fields()
            if vr_rubr != 0:
                item_buff.update(
                    {
                        "start_validity": self.start_validity(),
                        "end_validity": self.end_validity(),
                        "competence_month": self._period.mes,
                        "competence_year": self._period.ano,
                        "registry_person": self.registry_person(),
                        "_class_": DemonstrativeItem,
                        "oid": str(entry.pk),
                        "cod_rubr": entry.evento.numero,
                        "oid_rubr": oid_rubr,
                        "ide_tab_rubr": tab_rubr,
                        "qtd_rubr": (
                            round(entry.qnt, 2)
                            if entry.qnt and round(entry.qnt, 2)
                            else None
                        ),
                        "fator_rubr": (
                            round(entry.pct, 2)
                            if entry.pct and round(entry.pct, 2)
                            else None
                        ),
                        "vr_rubr": round(abs(vr_rubr), 2),
                        # FIXME: DEFINIR COM DGPFP ind_apur_ir
                        # TODO: AVALIAR MOS ESOCIAL NO ITEM 10
                        "ind_apur_ir": 0,
                        "tp_proc_ret": self.tp_proc_ret(entry),
                        "nr_proc_ret": self.nr_proc_ret(entry),
                        "cod_susp": self.cod_susp(entry),
                        "vlr_rend_susp": self.vlr_rend_susp(entry),
                    }
                )
                createds.append(item_buff)
            else:
                msg = f"{entry} foi removida do demonstrativo pois o seu valor zerou em função do ajuste."
                msg += f" {PessoaFisica.objects.get(cpf=self.registry_person())} - {self.registry_person()}"
                msg += f" | {self._period.mes}/{self._period.ano}"
                self.task_info(msg=msg, type_of=2)

        generate_adjust_remun(createds, total_adjust)

        self._dm_dev_infos.update(
            {
                self.oid_paycheck(paycheck, rra=rra): {
                    "info_pgto_vr_liq": total_net,
                    "rra_prazo": rra_prazo,
                    "rra_installments_paid": rra_installments_paid,
                }
            }
        )

        return createds

    def _ide_period_query_per_ant(self, paycheck, rra=False):
        """Este método retorna os lançamentos de períodos anteriores quando o contracheque é do mesmo mês de avaliação.
        Retorna queryset none() quando for de mês diferente.

        Returns:
            FolhaEvento.queryset:"""
        if (
            self._period.mes == paycheck.folha.periodo.mes
            and self._period.ano == paycheck.folha.periodo.ano
        ):
            return self.entries_by_reference_per_ant_esocial(
                paycheck,
                paycheck.folha.periodo.mes,
                paycheck.folha.periodo.ano,
                rra=rra,
            ).filter(servidor__pessoa_fisica__cpf=self._instance_outside.cpf)
        return paycheck.lancamentos.none()

    def ide_periodo(
        self, ide_adc, paycheck, per_apur=False, ide_period_cls=None, rra=False
    ):
        createds = []
        exists_per_ref12 = []
        for period in (
            self._ide_period_query_per_ant(paycheck, rra=rra)
            .values("folha__periodo__pk", "reference_month", "reference_year")
            .order_by("folha__periodo__pk", "reference_year", "reference_month")
            .distinct()
        ):
            ide_periodo_per_ref = (
                f'{period.get("reference_year")}-{period.get("reference_month"):02d}'
            )

            if period.get("reference_month") == 12:
                exists_per_ref12.append(period.get("reference_year"))

            if period.get("reference_month") == 13:
                ide_periodo_per_ref = f'{period.get("reference_year")}-12'
                """Evita que o mês 13/ano seja adicionado se o 12/ano já tiver sido feito. Pois os eventos de 13 estão em 12."""
                if period.get("reference_year") in exists_per_ref12:
                    continue

            if not ide_adc:
                """Poderá ser o pk do Periodo apenas quando vier de S1202 e S1207."""
                ide_adc = (period.get("folha__periodo__pk"), "")

            period_buff = self.define_base_fields()
            period_buff.update(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "competence_month": period.get("reference_month"),
                    "competence_year": period.get("reference_year"),
                    "registry_person": self.registry_person(),
                    "_class_": ide_period_cls if ide_period_cls else IdePeriod,
                    "oid": f"{period.get('reference_month')}{period.get('reference_year'):02d}",
                    "ide_periodo_per_ref": ide_periodo_per_ref,
                    "ide_adc": self.ide_adc_str(ide_adc),
                    "info_per_ant_ide_estab_lot": self.ide_estab_lot(
                        paycheck,
                        period.get("reference_month"),
                        period.get("reference_year"),
                        ide_adc=ide_adc,
                        per_apur=per_apur,
                        rra=rra,
                    ),
                }
            )
            createds.append(period_buff)
        return createds

    @classmethod
    def ide_adc_str(cls, ide_adc):
        ide_adc_str = None
        if ide_adc:
            if type(ide_adc[0]) is not int:
                ide_adc_str = f"{ide_adc[0].strftime('%Y%m%d')}{ide_adc[1]}"
            else:
                ide_adc_str = f"{ide_adc[0]}"
        return ide_adc_str

    def tp_proc_ret(self, entry):
        if self.start_validity() >= DATE_V12:
            return entry.vars.get("tpProcRet", None)
        return None

    def nr_proc_ret(self, entry):
        if self.start_validity() >= DATE_V12:
            return entry.vars.get("nrProcRet", None)
        return None

    def cod_susp(self, entry):
        if self.start_validity() >= DATE_V12:
            return entry.vars.get("codSusp", None)
        return None

    def vlr_rend_susp(self, entry):
        vlr_rend_susp = entry.vars.get("vlrRendSusp", None)
        if self.start_validity() >= DATE_V12 and vlr_rend_susp:
            return round(decimal.Decimal(vlr_rend_susp), 2)
        return None


class S1200Factory(Factory):

    EXTRACTED_MODEL_CLASS = S1200
    EXTRACTOR = S1200Extractor

    @classmethod
    def _get_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        return cls.EXTRACTOR._get_oid(instance_outside, **kwargs)

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        period = kwargs.get("period")
        query = PessoaFisica.objects.filter(
            Q(servidor__paychecks__folha__periodo__mes=period.mes)
            & Q(servidor__paychecks__folha__periodo__ano=period.ano)
        ).filter(cls._filter_specialized())

        exclude_specialized = cls._exclude_specialized()
        if exclude_specialized:
            query = query.exclude(exclude_specialized)

        return query.distinct()

    @classmethod
    def _filter_specialized(cls):
        """Este método retorna um filter lookup que será aplicado em filter de _query_instance_outside.
        Neste caso retorna todos do regime definido no extrator ou colaboradores eventuais do RGPS.

        Returns:
            (generator)"""
        # query_occasional_collaborator = (pk for pk in SocialSecurityEmployee.objects.filter(
        #     employee__type_by_possession='COE', social_security_config__regime=1).values_list('employee__pessoa_fisica__pk', flat=True))

        return Q(
            servidor__socialsecurities__social_security_config__regime__in=cls.EXTRACTOR.REGIME
        ) | Q(servidor__type_by_possession="COE")

    @classmethod
    def _exclude_specialized(cls):
        """Este método retorna um filter lookup que será aplicado em exclude de _query_instance_outside.
        Neste caso exclue os beneficiários.

        Returns:
            (generator)"""
        # return Q(servidor__type_by_possession__in=TYPE_BY_POSSESSION_BENEFICIARY)
        return None
