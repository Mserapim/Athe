# -*- coding: utf-8 -*-
from datetime import date

from django.db.models import Q, Sum

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from esocial.extractors.registrationbaseworker import vinculo_tp_reg_prev
from esocial.extractors.s1200 import S1200Extractor, S1200Factory
from esocial.models import (
    S1200,
    S1202,
    S1207,
    S1210,
    DedDependente,
    DedPenAlim,
    Demonstrative,
    Demonstrative1202,
    Demonstrative1207,
    DemonstrativeItem,
    Event,
    InfoDepSau,
    InfoIRDepedente,
    InfoIRPrevidCompl,
    InfoIRProcRet,
    InfoIrComplemen,
    InfoIrCr,
    InfoPgto,
    InfoPlanSaude,
    InfoValoresProcRet,
    get_current_config,
    task_info,
)
from esocial.utils import agrupador_lancamentos_pensao
from rh.const import DEPENDENCY_INCOME_TAX, TYPE_BY_POSSESSION_BENEFICIARY
from rh.gfp.models import IRRF, ContraCheque, Evento, FolhaEvento
from rh.models import Dependente, PessoaFisica, PessoaJuridica, Servidor
from rh.models import Servidor as Employee
from rh.models import SocialSecurityEmployee

log = getLogger(__name__)

TP_CR_IR_RRA = "188901"
TP_CR_IR_MENSAL = "056107"
TP_CR_IR_BENEFICIO = "353301"

TP_PREV_COMPLEMEN = 3

ID_PREV_COMPLEM = 1224938

GENERO_IRRF_13 = "991"
GENERO_IRRF_RRA = "992"
GENERO_IRRF_FERIAS = "993"
GENERO_IRRF_MENSAL = "999"
GENERO_PENSAO = "706"


GENERO_PREV_COMPLM = "912"
GENERO_PREV_COMPLM_13 = "913"

NAME_TAGS = "EVENT_TAGS"

TAG_PREV_COMPLM = "prev-complementar-esocial"
TAG_PREV_COMPLM13 = "prev-complementar13-esocial"
TAG_PEN_ALIM_MENSAL = "pen-alim-mensal-esocial"
TAG_PEN_ALIM_13 = "pen-alim-13-esocial"
TAG_PEN_ALIM_FERIAS = "pen-alim-ferias-esocial"
TAG_PEN_ALIM_RRA = "pen-alim-rra-esocial"

TIPO_REND_TAG_PEN_ALIM = {
    TAG_PEN_ALIM_MENSAL: "11",
    TAG_PEN_ALIM_13: "12",
    TAG_PEN_ALIM_FERIAS: "13",
    TAG_PEN_ALIM_RRA: "18",
}

TAGS_TP_CR_PEN = {
    TP_CR_IR_MENSAL: [TAG_PEN_ALIM_MENSAL, TAG_PEN_ALIM_13, TAG_PEN_ALIM_FERIAS],
    TP_CR_IR_BENEFICIO: [TAG_PEN_ALIM_MENSAL, TAG_PEN_ALIM_13, TAG_PEN_ALIM_FERIAS],
    TP_CR_IR_RRA: [TAG_PEN_ALIM_RRA],
}

TIPO_REND = {
    GENERO_IRRF_MENSAL: "11",
    GENERO_IRRF_13: "12",
    GENERO_IRRF_FERIAS: "13",
    GENERO_IRRF_RRA: "18",
}

COD_ESOCIAL_CONVENIO_SAUDE = 9219

CNPJ_COVENIO_UNIMED = "03533726000188"
COD_ANS_CONVENIO_UNIMED = 342084

TP_DEPENDENTE_PLAN_SAUDE = 2


class S1210Extractor(S1200Extractor):

    REGIME = (1, 2, 3)

    def __init__(self, instance_outside, *args, **kwargs):
        super().__init__(instance_outside, *args, **kwargs)

    @classmethod
    def paychecks(cls, month, year, registry_person=None):
        """Este método
        Args:
            month (int): quando 13 modifica para 12
            year (int):
            registry_person (str): cpf da pessoa física

        Returns:
            values_list('pk')
        """
        paychecks = ContraCheque.objects.filter(
            servidor__pessoa_fisica__cpf=registry_person,
            folha__dt_pagamento__month=12 if month == 13 else month,
            folha__dt_pagamento__year=year,
            folha__status__in=(3, 4),
            pensioner__isnull=True,
        ).exclude(total_liquido__lt=0)

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

        def _employees():
            # TODO: VERIFICAR SE É NECESSÁRIO EXCLUIR POR FALTA DE SOCIALSECUTIRY
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

        return paychecks.filter(
            Q(servidor__pk__in=_employees()) | Q(servidor__type_by_possession="COE")
        )

    def demonstratives1200(self):
        demonstratives = Demonstrative.objects.filter(
            s1200__pk__in=(
                pk
                for pk in S1200.objects.valids_by_status()
                .filter(registry_person=self.registry_person())
                .exclude(is_invalid_cache=True)
                .values_list("pk", flat=True)
            ),
            info_pgto_dt_pgto__range=(self._period.start_date, self._period.end_date),
        )
        return self.filter_demonstratives(demonstratives)

    def demonstratives1202(self):
        demonstratives = Demonstrative1202.objects.filter(
            s1202__pk__in=(
                pk
                for pk in S1202.objects.valids_by_status()
                .filter(registry_person=self.registry_person())
                .exclude(is_invalid_cache=True)
                .values_list("pk", flat=True)
            ),
            info_pgto_dt_pgto__range=(self._period.start_date, self._period.end_date),
        )
        return self.filter_demonstratives(demonstratives)

    def demonstratives1207(self):
        demonstratives = Demonstrative1207.objects.filter(
            s1207__pk__in=(
                pk
                for pk in S1207.objects.valids_by_status()
                .filter(registry_person=self.registry_person())
                .exclude(is_invalid_cache=True)
                .values_list("pk", flat=True)
            ),
            info_pgto_dt_pgto__range=(self._period.start_date, self._period.end_date),
        )
        return self.filter_demonstratives(demonstratives)

    def filter_demonstratives(self, demonstratives):
        config = get_current_config()
        demonstratives = demonstratives.exclude(
            registry_employee__in=(
                registry
                for registry in config.employee_exclude.filter(
                    pessoa_fisica__cpf=self.registry_person()
                ).values_list("matricula", flat=True)
            )
        )

        if config.employee_filter.filter(
            pessoa_fisica__cpf=self.registry_person()
        ).exists():
            demonstratives = demonstratives.filter(
                registry_employee__in=(
                    registry
                    for registry in config.employee_filter.filter(
                        pessoa_fisica__cpf=self.registry_person()
                    ).values_list("matricula", flat=True)
                )
            )
        return demonstratives

    @classmethod
    def _previous_event_not_send(cls, event):
        """Este método retorna o último evento anterior ao extraído, de mesmo oid e acronym, não enviado."""
        return (
            Event.objects.valids_not_sent()
            .filter(
                oid=event.oid,
                acronym__in=("s1200", "s1202", "s1207"),
                start_validity=event.start_validity,
                registry_person=event.registry_person,
            )
            .order_by("-start_validity")
        )

    @classmethod
    def _get_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        month = kwargs.get("month", "*")
        year = kwargs.get("year", "*")
        if month == 13:
            month = 12
        return f"{year}{month:02d}{instance_outside.cpf}"

    def ide_evento_per_apur(self):
        """Informar o mês/ano (formato AAAA-MM) de referência
        das informações.
        Validação: Deve ser um mês/ano válido, igual ou
        posterior ao início da obrigatoriedade dos eventos
        periódicos para o empregador."""
        return "{}-{:02d}".format(
            self.start_validity().year, self.start_validity().month
        )

    @classmethod
    def _get_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        month = kwargs.get("month", "*")
        year = kwargs.get("year", "*")
        if month == 13:
            month = 12
        return f"{year}{month:02d}{instance_outside.cpf}"

    def competence_month(self):
        return 12 if self._period.mes == 13 else self._period.mes

    def ide_evento_per_apur(self):
        """Informar o mês/ano (formato AAAA-MM) de referência
        das informações.
        Validação: Deve ser um mês/ano válido, igual ou
        posterior ao início da obrigatoriedade dos eventos
        periódicos para o empregador."""
        return "{}-{:02d}".format(
            self.start_validity().year, self.start_validity().month
        )

    def ide_benef_cpf_benef(self):
        return self.ide_trabalhador_cpf_trab()

    def gen_info_pgto(self, demonstrative, info_pgto_tp_pgto, per_ref):
        """Este método gera um InfoPgto.

        Args:
            demonstrative (Demonstrative, Demonstrative1202, Demonstrative1207): Demonstrativo de pagamento.
            info_pgto_tp_pgto (int): _description_
            per_ref (str): _description_
        """

        if (
            demonstrative.info_pgto_vr_liq is not None
            and demonstrative.info_pgto_vr_liq >= 0
        ):
            info_buff = self.define_base_fields()
            info_buff.update(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "competence_month": self._period.mes,
                    "competence_year": self._period.ano,
                    "registry_person": self.registry_person(),
                    "registry_employee": demonstrative.registry_employee,
                    "_class_": InfoPgto,
                    "oid": demonstrative.oid,
                    "info_pgto_dt_pgto": demonstrative.info_pgto_dt_pgto,
                    "info_pgto_tp_pgto": info_pgto_tp_pgto,
                    "info_pgto_per_ref": per_ref,
                    "info_pgto_ide_dm_dev": demonstrative.oid,
                    "info_pgto_vr_liq": demonstrative.info_pgto_vr_liq,
                    "info_pgto_ext_ind_nif": None,
                    "info_pgto_ext_nif_benef": None,
                    "info_pgto_ext_frm_tribut": None,
                    "end_ext_end_dsc_lograd": None,
                    "end_ext_end_nr_lograd": None,
                    "end_ext_end_complem": None,
                    "end_ext_end_bairro": None,
                    "end_ext_end_cidade": None,
                    "end_ext_end_estado": None,
                    "end_ext_end_cod_postal": None,
                    "end_ext_telef": None,
                }
            )
            self._dm_dev.append(info_buff)

    def info_pgto(self):
        self._dm_dev = []

        initial_group_date = self.initial_group_date()
        initial_group_date = date(initial_group_date.year, initial_group_date.month, 1)

        def gen_demonstratives(demonstratives):
            for demonstrative in demonstratives:
                per_ref = demonstrative.ide_evento_per_apur
                if len(per_ref) == 4:
                    per_ref_date = date(int(per_ref), 12, 1)
                else:
                    per_ref_date = date(
                        int(per_ref.split("-")[0]), int(per_ref.split("-")[1]), 1
                    )

                if per_ref_date >= initial_group_date:
                    employee = demonstrative.employee()
                    info_pgto_tp_pgto = self.info_pgto_tp_pgto(
                        employee,
                        12 if self._period.mes == 13 else self._period.mes,
                        self._period.ano,
                    )
                    self.gen_info_pgto(demonstrative, info_pgto_tp_pgto, per_ref)

        gen_demonstratives(self.demonstratives1200())
        gen_demonstratives(self.demonstratives1202())
        gen_demonstratives(self.demonstratives1207())

        return self._dm_dev

    def info_pgto_tp_pgto(self, employee, month, year):
        if self.tp_pgto_beneficiary(employee):
            return 5
        return self.tp_pgto_employee(employee, month, year)

    def tp_pgto_employee(self, employee, month, year):
        tp = None
        if employee.is_occasional_collaborator:
            tp = vinculo_tp_reg_prev(employee)
        else:
            sses = SocialSecurityEmployee.objects.filter(employee=employee)
            dr = NewDateRange.from_month(year, month)
            sse = sses.currents_in(range=dr)
            if not sse.exists():
                sse = sses.filter(
                    Q(employee__termination_date__isnull=False)
                    & Q(employee__termination_date__lt=dr.first)
                )
            sse = sse.last()
            if sse and sse.social_security_config.regime:
                tp = sse.social_security_config.regime

        return MAP_REGIME_TP_PGTO.get(tp, None)

    def tp_pgto_beneficiary(self, employee):
        return employee.type_by_possession in TYPE_BY_POSSESSION_BENEFICIARY

    @classmethod
    def total_ir_paycheck(cls, month, year, registry_person=None, task=None):
        """Calcula total de eventos IR em Config.events_ir.

        Args:
            month (int): _description_
            year (int): _description_
            registry_person (str, optional): _description_. Defaults to None.
            task (mq.Task, optional): _description_. Defaults to None.

        Returns:
            decimal: total
        """
        tag = "irrf-esocial"

        events_ir = list(
            Evento.objects.filter(tags__label=tag).values_list("numero", flat=True)
        )

        entries = cls.all_entries_by_reference_esocial(
            month, year, registry_person=registry_person
        ).filter(evento__numero__in=events_ir)

        if month == 12:
            entries_13 = cls.all_entries_by_reference_esocial(
                13, year, registry_person=registry_person
            ).filter(evento__numero__in=events_ir)
            entries = FolhaEvento.objects.filter(
                Q(pk__in=(pk for pk in entries.values_list("pk", flat=True)))
                | Q(pk__in=(pk for pk in entries_13.values_list("pk", flat=True)))
            )

        entries = entries.distinct()

        total = entries.aggregate(sum_valor=Sum("valor")).get("sum_valor") or 0

        if not entries.exists():
            events_ir = list(
                Evento.objects.filter(tags__label=tag).values_list("numero", flat=True)
            )

            employee = Employee.objects.filter(pessoa_fisica__cpf=registry_person)
            if employee.filter(ativo=True).exists():
                employee = employee.filter(ativo=True).last()
            else:
                employee = employee.last()

            msg = f"{employee.type_by_possession} - {employee}"
            msg += f" - Não possui IR na Folha ({month}/{year}) | Eventos {tag}: {events_ir}."
            task_info(task, msg=msg, type_of=2)
        return total

    def info_ir_complemen(self):
        ir_complem = []

        info_ir_cr, info_dep, info_plan_saude = self.gen_info_ir_complemen()

        ir_complem.append(
            {
                "start_validity": self.start_validity(),
                "end_validity": self.end_validity(),
                "competence_month": self._period.mes,
                "competence_year": self._period.ano,
                "registry_person": self.registry_person(),
                "_class_": InfoIrComplemen,
                "oid": self.oid(),
                "info_ir_dependente": info_dep,
                "info_ir_complem_dt_laudo": self.info_dt_molestia(
                    self._instance_outside.employee
                ),
                "info_ir_cr": info_ir_cr,
                "info_plan_saude": info_plan_saude,
            }
        )
        return ir_complem

    def get_oid_rra(self, demonstrativo):
        oid = demonstrativo.oid
        if demonstrativo.rra:
            len_id_rra = len(str(demonstrativo.rra))
            oid = int(demonstrativo.oid[:-len_id_rra])
        return oid

    def gen_info_ir_complemen(self):
        self._info_irrf_cr = []
        self._prev_complem_dict = {}
        self._info_dep = []
        self._info_plan_saude = []

        inicio_grupo_datas = self.initial_group_date()
        inicio_grupo_datas = date(inicio_grupo_datas.year, inicio_grupo_datas.month, 1)

        self.prev_complem = PessoaJuridica.objects.get(pk=ID_PREV_COMPLEM)

        self.demostrativo_servidor = None

        def gen_demonstrativos(demonstrativos):
            for demonstrativo in demonstrativos:
                if not self.demostrativo_servidor:
                    self.demostrativo_servidor = demonstrativo.employee()
                per_ref = demonstrativo.ide_evento_per_apur
                if len(per_ref) == 4:
                    per_ref_data = date(int(per_ref), 12, 1)
                else:
                    per_ref_data = date(
                        int(per_ref.split("-")[0]), int(per_ref.split("-")[1]), 1
                    )

                if per_ref_data >= inicio_grupo_datas:
                    oid = self.get_oid_rra(demonstrativo)
                    contracheque = ContraCheque.objects.get(pk=oid)
                    self.gen_info_ir_cr(demonstrativo, contracheque)

        gen_demonstrativos(self.demonstratives1200())
        gen_demonstrativos(self.demonstratives1202())
        gen_demonstrativos(self.demonstratives1207())

        self.gen_info_ir_dependente(self.demostrativo_servidor)
        self.gen_info_plan_saude_dependente(self.demostrativo_servidor)
        self.gen_info_plan_saude(self.demostrativo_servidor)

        return self._info_irrf_cr, self._info_dep, self._info_plan_saude

    def gen_info_plan_saude(self, servidor):
        lancamento_saude = self.lancamento_plano_saude(servidor)
        if lancamento_saude:
            self._info_plan_saude.append(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "competence_month": self._period.mes,
                    "competence_year": self._period.ano,
                    "registry_person": self.registry_person(),
                    "_class_": InfoPlanSaude,
                    "plan_saude_cnpj_oper": CNPJ_COVENIO_UNIMED,
                    "plan_saude_reg_ans": COD_ANS_CONVENIO_UNIMED,
                    "plan_saude_vlr_saude_tit": lancamento_saude.correct_valor,
                    "info_dep_saude": self.info_dep_saude(servidor),
                }
            )

    def info_dep_saude(self, servidor):
        dados = []
        lancamentos_agregados = self.lancamentos_plano_saude_agregados(servidor)
        for lancamento_agregado in lancamentos_agregados:
            dados.append(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "competence_month": self._period.mes,
                    "competence_year": self._period.ano,
                    "registry_person": self.registry_person(),
                    "_class_": InfoDepSau,
                    "info_dep_sau_cpf_dep": lancamento_agregado.info,
                    "info_dep_sau_vlr_saude_dep": lancamento_agregado.correct_valor,
                }
            )

        return dados

    def gen_info_ir_dependente(self, servidor):
        pensionistas = servidor.pensao_pagador.all()
        for pen in pensionistas:
            self._info_dep.append(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "competence_month": self._period.mes,
                    "competence_year": self._period.ano,
                    "registry_person": self.registry_person(),
                    "_class_": InfoIRDepedente,
                    "info_dep_cpf_dep": pen.pensionista.cpf,
                    "info_dep_dt_nascto": pen.pensionista.data_nascimento,
                    "info_dep_nome": pen.pensionista.nome,
                    "info_dep_dep_irrf": None,
                    "info_dep_tp_dep": None,
                    "info_dep_descr_dep": None,
                }
            )
        return self._info_dep

    def gen_info_plan_saude_dependente(self, servidor):
        from datetime import datetime

        data_atual = datetime.today().date()
        dependentes = Dependente.objects.filter(
            Q(
                servidor=servidor,
                dependencias__tipo=TP_DEPENDENTE_PLAN_SAUDE,
                dependencias__data_inicio__lte=data_atual,
            )
            & (
                Q(dependencias__data_fim__isnull=True)
                | Q(dependencias__data_fim__gte=data_atual)
            )
        )
        for depedente in dependentes:
            self._info_dep.append(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "competence_month": self._period.mes,
                    "competence_year": self._period.ano,
                    "registry_person": self.registry_person(),
                    "_class_": InfoIRDepedente,
                    "info_dep_cpf_dep": depedente.pessoa_fisica.cpf,
                    "info_dep_dt_nascto": depedente.pessoa_fisica.data_nascimento,
                    "info_dep_nome": depedente.pessoa_fisica.nome,
                    "info_dep_dep_irrf": None,
                    "info_dep_tp_dep": None,
                    "info_dep_descr_dep": None,
                }
            )
        return self._info_dep

    def gen_info_ir_cr(self, demonstrativo, contracheque):
        irrf_dados = {}
        ir_tp_cr = self.get_info_ircr_tp_cr(demonstrativo, contracheque)
        lancamentos_pensao = self.lancamentos_pensao(demonstrativo, ir_tp_cr)
        lancamentos_prev = self.gen_previd_compl(contracheque)
        irrf_dados.update(
            {
                "oid": ir_tp_cr,
                "start_validity": self.start_validity(),
                "end_validity": self.end_validity(),
                "competence_month": self._period.mes,
                "competence_year": self._period.ano,
                "registry_person": self.registry_person(),
                "_class_": InfoIrCr,
                "info_ircr_tp_cr": ir_tp_cr,
                "ded_dependente": self.gen_ded_depen(contracheque),
                "ded_pen_alim": self.gen_ded_pen_alim(lancamentos_pensao),
                "info_ir_previd_compl": (
                    [self._prev_complem_dict] if lancamentos_prev else []
                ),
                "info_ir_proc_ret": self.info_ir_proc_ret(demonstrativo),
            }
        )

        self._info_irrf_cr.append(irrf_dados)

    def gen_ded_depen(self, contracheque):
        dados = []
        servidor = contracheque.servidor
        ded_valor = self.get_ded_depen_vlr_ded_dep()
        generos_lancamentos_ir = list(
            contracheque.lancamentos.filter(
                evento__genre_event__genre_number__in=[
                    GENERO_IRRF_13,
                    GENERO_IRRF_RRA,
                    GENERO_IRRF_FERIAS,
                    GENERO_IRRF_MENSAL,
                ]
            ).values_list("evento__genre_event__genre_number", flat=True)
        )
        generos_lancamentos_values = list(set(generos_lancamentos_ir))

        for genero_lancamento in generos_lancamentos_values:
            tp_rend = TIPO_REND.get(genero_lancamento, None)
            for dependente in servidor.dependentes.filter(
                dependencias__tipo=DEPENDENCY_INCOME_TAX
            ):
                dados.append(
                    {
                        "oid": f"{tp_rend}{dependente.pessoa_fisica.cpf}",
                        "start_validity": self.start_validity(),
                        "end_validity": self.end_validity(),
                        "competence_month": self._period.mes,
                        "competence_year": self._period.ano,
                        "registry_person": self.registry_person(),
                        "_class_": DedDependente,
                        "ded_depen_tp_rend": tp_rend,
                        "ded_depen_cpf_dep": dependente.pessoa_fisica.cpf,
                        "ded_depen_vlr_ded_dep": ded_valor,
                    }
                )
        return dados

    def gen_ded_pen_alim(self, lancamentos):
        dados = []
        if lancamentos:
            lancamentos = lancamentos.values(
                "evento__tags__label", "correct_valor", "cid"
            )
            lancamentos_agrupados = agrupador_lancamentos_pensao(lancamentos)
            for lancamento in lancamentos_agrupados:
                dados.append(
                    {
                        "start_validity": self.start_validity(),
                        "end_validity": self.end_validity(),
                        "competence_month": self._period.mes,
                        "competence_year": self._period.ano,
                        "registry_person": self.registry_person(),
                        "_class_": DedPenAlim,
                        "pen_alim_tp_rend": TIPO_REND_TAG_PEN_ALIM.get(
                            lancamento["tag"], None
                        ),
                        "pen_alim_cpf_dep": self.buscar_pensionista_cpf(
                            lancamento["cid"]
                        ),
                        "pen_alim_vlr_ded_pen_alim": lancamento["total_pens"],
                    }
                )
        return dados

    def gen_previd_compl(self, contracheque):
        eventos_prev_compl = Evento.objects.filter(
            tags__label__in=[TAG_PREV_COMPLM, TAG_PREV_COMPLM13], tags__name=NAME_TAGS
        ).values_list("pk", flat=True)
        lancamentos_prev = contracheque.lancamentos.filter(
            evento__pk__in=eventos_prev_compl
        )
        for lancamento in lancamentos_prev:
            is_decimo_terceiro = lancamento.evento.tags.filter(
                label="prev-complementar13-esocial"
            ).exists()

            if not self._prev_complem_dict:
                self._prev_complem_dict.update(
                    {
                        "start_validity": self.start_validity(),
                        "end_validity": self.end_validity(),
                        "competence_month": self._period.mes,
                        "competence_year": self._period.ano,
                        "registry_person": self.registry_person(),
                        "_class_": InfoIRPrevidCompl,
                        "previd_compl_tp_prev": TP_PREV_COMPLEMEN,
                        "previd_compl_cnpj_entid_pc": self.prev_complem.cnpj,
                    }
                )

            if is_decimo_terceiro:
                self._prev_complem_dict.update(
                    {
                        "previd_compl_vlr_ded_pc13": abs(lancamento.correct_valor),
                        "previd_compl_vlr_patroc_funp13": abs(
                            lancamento.correct_patronal
                        ),
                    }
                )
            else:
                self._prev_complem_dict.update(
                    {
                        "previd_compl_vlr_ded_pc": abs(lancamento.correct_valor),
                        "previd_compl_vlr_patroc_funp": abs(
                            lancamento.correct_patronal
                        ),
                    }
                )

        return lancamentos_prev

    def info_ir_proc_ret(self, demonstrativo):
        info_proc_data = []

        if hasattr(demonstrativo, "nr_proc_ret"):
            if demonstrativo.tp_proc_ret is not None:
                info_proc_data.append(
                    {
                        "start_validity": self.start_validity(),
                        "end_validity": self.end_validity(),
                        "competence_month": self._period.mes,
                        "competence_year": self._period.ano,
                        "registry_person": self.registry_person(),
                        "_class_": InfoIRProcRet,
                        "oid": demonstrativo.nr_proc_ret,
                        "info_proc_ret_tp_proc_ret": demonstrativo.tp_proc_ret,
                        "info_proc_ret_nr_proc_ret": demonstrativo.nr_proc_ret,
                        "info_proc_ret_cod_susp": demonstrativo.cod_susp,
                        "info_valores_proc_ret": self.info_valores(demonstrativo),
                    }
                )

        return info_proc_data

    def info_valores(self, demonstrativo):
        vr_rubr = None
        vlr_rend_susp = None
        if hasattr(demonstrativo, "vr_rubr"):
            vr_rubr = demonstrativo.vr_rubr
        if hasattr(demonstrativo, "vlr_rend_susp"):
            vlr_rend_susp = demonstrativo.vlr_rend_susp
        return [
            {
                "start_validity": self.start_validity(),
                "end_validity": self.end_validity(),
                "competence_month": self._period.mes,
                "competence_year": self._period.ano,
                "registry_person": self.registry_person(),
                "_class_": InfoValoresProcRet,
                "oid": demonstrativo.oid,
                "info_valores_ind_apuracao": demonstrativo.ide_evento_ind_apuracao,
                "info_valores_vlr_n_retido": vr_rubr,
                "info_valores_vlr_dep_jud": None,
                "info_valores_vlr_cmp_ano_cal": None,
                "info_valores_vlr_cmp_ano_ant": None,
                "info_valores_vlr_rend_susp": vlr_rend_susp,
                "ded_susp_proc_ret": None,
            }
        ]

    def get_info_ircr_tp_cr(self, demonstrativo, contracheque):
        # lancamentos_rra = contracheque.lancamentos.filter(rra_employee__isnull=False)
        if demonstrativo.rra:
            return TP_CR_IR_RRA
        else:
            employee = demonstrativo.employee()
            benefit = self.tp_pgto_beneficiary(employee)
            if benefit:
                return TP_CR_IR_BENEFICIO

            return TP_CR_IR_MENSAL

    def get_ded_depen_tp_rend(self, lancamento):
        genero_numero = lancamento.evento.genre_event.genre_number
        return TIPO_REND.get(genero_numero, None)

    def get_ded_depen_vlr_ded_dep(self):
        irrf = IRRF.objects.first()
        return irrf.valor_dependente

    def info_dt_molestia(self, servidor):
        if servidor.molestia:
            return servidor.molestia.data_laudo
        return None

    def lancamentos_pensao(self, demonstrativo, ir_tp_cr):
        tags = TAGS_TP_CR_PEN.get(ir_tp_cr, [])
        if not tags:
            return tags
        lancamentos_pensao = FolhaEvento.objects.filter(
            servidor=demonstrativo.employee(),
            folha__periodo__mes=self._period.mes,
            folha__periodo__ano=self._period.ano,
            evento__tags__label__in=tags,
        ).distinct()

        return lancamentos_pensao

    def lancamento_plano_saude(self, servidor):
        lancamento_saude = FolhaEvento.objects.filter(
            servidor=servidor,
            folha__periodo__mes=self._period.mes,
            folha__periodo__ano=self._period.ano,
            evento__configs__nature_event__code=COD_ESOCIAL_CONVENIO_SAUDE,
            info=servidor.pessoa_fisica.cpf,
        )

        return lancamento_saude.first()

    def lancamentos_plano_saude_agregados(self, servidor):
        lancamentos_saude = FolhaEvento.objects.filter(
            servidor=servidor,
            folha__periodo__mes=self._period.mes,
            folha__periodo__ano=self._period.ano,
            evento__configs__nature_event__code=COD_ESOCIAL_CONVENIO_SAUDE,
            evento__tags__label="plan-saude-agregados-esocial",
        )

        return lancamentos_saude

    def buscar_pensionista_cpf(self, cid):
        pensionista = PessoaFisica.objects.get(pk=cid)
        if pensionista:
            return pensionista.cpf
        return None


MAP_REGIME_TP_PGTO = {
    1: 1,  # RGPS
    2: 4,  # RPPS
    3: 4,
}


class S1210Factory(S1200Factory):

    EXTRACTED_MODEL_CLASS = S1210
    EXTRACTOR = S1210Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        period = kwargs.get("period")
        query = PessoaFisica.objects.filter(
            servidor__paychecks__folha__dt_pagamento__range=(
                period.start_date,
                period.end_date,
            )
        ).filter(cls._filter_specialized())

        exclude_specialized = cls._exclude_specialized()
        if exclude_specialized:
            query = query.exclude(exclude_specialized)

        return query.distinct()

    @classmethod
    def _filter_specialized(cls):
        """Este método retorna um filter lookup que será aplicado em filter de _query_instance_outside.
        Neste caso retorna todos do regime definido no extrator e colaboradores eventuais do RPPS.

        Returns:
            (generator)"""
        return Q(
            servidor__socialsecurities__social_security_config__regime__in=cls.EXTRACTOR.REGIME
        ) | Q(servidor__type_by_possession="COE")

    @classmethod
    def _exclude_specialized(cls):
        """Este método retorna um generator dos pks das pessoas que serão incluídas no query_instances_outside.

        Returns:
            (generator)"""
        return ()
