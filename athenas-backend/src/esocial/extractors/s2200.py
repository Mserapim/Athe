# -.- coding: utf-8 -.-
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from esocial.const import DIFF_VALIDITY_END, NOTHING_TODO
from esocial.extractors.base import Factory
from esocial.extractors.registrationbaseworker import WorkerBaseExtractor
from esocial.models import S2200, ItemTable, get_current_config
from rh.afastamento.models import AfastamentoOutroOrgao, BaseLicencaAfastamento
from rh.gfp.models import ExtraPaymentPeriod, ReferenciaSalario
from rh.models import MovimentacaoPosse, Servidor
from esocial.const import TYPE_VACATION

log = getLogger(__name__)


def valid_types():
    return [x.cvalue for x in ItemTable.objects.worker_table().choice.all()]


class S2200Extractor(WorkerBaseExtractor):

    VALIDITY_FIELDS = ["info_estatutario_dt_exercicio"]
    EXCLUDE_FIELDS_EQUALS = [
        "brasil_dsc_lograd",
        "brasil_complemento",
        "brasil_uf",
        "brasil_nr_lograd",
        "brasil_bairro",
        "brasil_cep",
        "brasil_tp_lograd",
        "brasil_cod_munic",
        "info_deficiencia_info_cota",
        "trabalhador_cpf_trab",
        "trabalhador_nm_trab",
        "trabalhador_sexo",
        "trabalhador_raca_cor",
        "trabalhador_est_civ",
        "trabalhador_grau_instr",
        "trabalhador_nm_soc",
        "nascimento_dt_nascto",
        "nascimento_pais_nascto",
        "nascimento_pais_nac",
        "exterior_pais_resid",
        "exterior_dsc_lograd",
        "exterior_nr_lograd",
        "exterior_complemento",
        "exterior_bairro",
        "exterior_nm_cid",
        "exterior_cod_postal",
        "trab_imig_tmp_resid",
        "trab_imig_cond_ing",
        "info_deficiencia_def_fisica",
        "info_deficiencia_def_visual",
        "info_deficiencia_def_auditiva",
        "info_deficiencia_def_mental",
        "info_deficiencia_def_intelectual",
        "info_deficiencia_reab_readap",
        "info_deficiencia_observacao",
        "contato_fone_princ",
        "contato_email_princ",
    ]

    def __init__(self, *args, **kwargs):
        super(S2200Extractor, self).__init__(*args, **kwargs)

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""
        references = []
        start_validity = None
        end_validity = None
        if self.check_reference_strong():
            _references_strong_start_date = self._references_strong_start_date()
            if _references_strong_start_date:
                start_validity = max(_references_strong_start_date)

                references = self._references()

                """definindo o fim com a data de desligamento"""
                _references_strong_end_date = self._references_strong_end_date(
                    start_validity=start_validity
                )
                if _references_strong_end_date:
                    end_validity = min(_references_strong_end_date)
        return start_validity, end_validity, references

    def _references(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return self._references_strong()

    def _references_strong(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return [self._instance_outside]

    def _references_strong_start_date(self):
        return [self._instance_outside.exercise_date]

    def _references_strong_end_date(self, start_validity=None):
        rs = []
        termination_date = self._termination_date(
            self._instance_outside, start_validity=start_validity
        )
        if termination_date:
            rs = [termination_date]
        return rs

    @classmethod
    def _termination_date(cls, instance_outside, start_validity=None):
        if instance_outside.type_by_possession in ("EFE", "ECM", "EFC"):
            termination_date = (
                instance_outside.posses.filter(
                    quadro__cargo__tipo_lei_cargo="EF",
                    data_exercicio=instance_outside.exercise_date,
                )
                .last()
                .data_desligamento
            )
            derived_possession = instance_outside.posses.filter(
                my_type__in=(
                    "movimentacaoreadaptacao",
                    "movimentacaoreconducao",
                    "movimentacaoreintegracao",
                    "movimentacaoreversao",
                )
            )

            if (
                derived_possession.exists()
                and termination_date
                and termination_date <= cls.initial_group_date()
            ):
                termination_date = derived_possession.last().data_desligamento
        else:
            termination_date = instance_outside.termination_date

        return termination_date

    @property
    def _class_config(self):
        """Esta propriedade retorna a classe da configuração utilizada como referência.

        Returns:
            class
        """
        return MovimentacaoPosse

    def _config(self):
        """Este método retorna o queryset básico da referência.

        Returns:
            queryset
        """
        return self._instance_outside.posses.filter(
            quadro__cargo__tipo_lei_cargo__in=("CM", "FC", "EF", "EL")
        ).only_original()

    def _get_cargo(self):
        """Este método retorna um CargoQuadro da posse de EF válido entre start_validity(exercise_date) e evaluate_date.
        A evaluate_date pode ser exercise_date ou initial_group_date.

        Returns:
            list of [MovimentacaoPosse, CargoQuadro, ConfigJobPosition]"""
        start_date = self.start_validity()
        end_date = self.start_validity()
        if start_date:
            if end_date < self.initial_group_date():
                end_date = self.initial_group_date()
            possession = (
                self._config()
                .filter(quadro__cargo__tipo_lei_cargo="EF")
                .assets_in(range=NewDateRange(start_date, end_date))
                .last()
            )
            if possession:
                config_job_position = possession.quadro.cargo.get_configs(
                    start_date=start_date, end_date=end_date
                ).last()
                return (
                    possession,
                    possession.quadro.job_position_chart,
                    config_job_position,
                )
        return None, None, None

    def _get_funcao(self):
        """Este método retorna um CargoQuadro da posse de CM, FC válido entre start_validity(exercise_date) e end_date.
        A end_date pode ser exercise_date ou initial_group_date.

        Returns:
            list of [MovimentacaoPosse, CargoQuadro, ConfigJobPosition]"""
        start_date = end_date = self.start_validity()
        if end_date and end_date < self.initial_group_date():
            start_date = end_date = self.initial_group_date()
        if start_date:
            possession = (
                self._config()
                .filter(quadro__cargo__tipo_lei_cargo__in=("CM", "FC", "EL"))
                .assets_in(range=NewDateRange(start_date, end_date))
                .last()
            )
            if possession:
                config_job_position = possession.quadro.cargo.get_configs(
                    start_date=start_date, end_date=end_date
                ).last()
                return (
                    possession,
                    possession.quadro.job_position_chart,
                    config_job_position,
                )
        return None, None, None

    def _references_next(self, start_validity=None):
        return []

    def _query_config_reference(self):
        """Este método retorna o queryset da referência. Definido

        Returns:
            queryset
        """
        if self._start_validity:
            query = self._config().assets_in(
                range=NewDateRange(
                    self._instance_outside.exercise_date,
                    self._instance_outside.exercise_date,
                )
            )
        else:
            query = self._class_config.objects.none()
        return query

    @classmethod
    def range_possessions(cls, registry):
        """Este método retorna um NewDateRange de todas as posses do servidor."""
        dr_possessions = NewDateRange()
        for mp in MovimentacaoPosse.objects.filter(
            servidor__matricula=registry
        ).exclude(requisicao__posse_origem__quadro__cargo__tipo_lei_cargo="AC"):
            data_desligamento = mp.data_desligamento
            if data_desligamento and mp.data_exercicio > data_desligamento:
                data_desligamento = (
                    data_desligamento - relativedelta(days=1)
                    if data_desligamento
                    else None
                )
            dr_possessions += NewDateRange(mp.data_exercicio, data_desligamento)
        return dr_possessions

    @classmethod
    def current_range_possession(cls, registry, date):
        """Este método retorna um NewDateRange da posse atual do servidor. Utiliza registry e date para definir o momento."""
        dr_possessions = cls.range_possessions(registry)
        for dr in dr_possessions.ranges():
            if dr[0] <= date <= dr[1]:
                return NewDateRange(dr[0], dr[1])
        return None

    def check_diff(self, diffs_content, diff_validity):
        """Este método é utilizado para modificar o pos_validate após diff_content e diff_validity estarem prontos.
        Cabe a cada extrator realizar a mudança e retornar um valor de retorno válido:
            NO_RESTRICTION, EXCLUDE_EVENT, DOESNT_EXIST_REFERENCE, NOTHING_TODO, SAME_EVENT, DIFF_VALIDITY_END_SAME_CONTENT,
            DIFF_VALIDITY_SAME_CONTENT, EQUAL_VALIDITY_DIFF_CONTENT, DIFF_VALIDITY_DIFF_CONTENT

        Args:
            diff_content (dict): dict de diff entre Event
            diff_validity (int): um dos valores: EQUAL_VALIDITY, DIFF_VALIDITY_END

        Returns:
            int: valor de retorno, default None(não interfere no pos_validate)
        """
        if not diffs_content and diff_validity == DIFF_VALIDITY_END:
            return NOTHING_TODO
        return None

    def check_reference_strong(self):
        """Este método verifica se existe uma referência forte para self._start_validity. Retorna True quando existir."""
        return (
            self._instance_outside and self._instance_outside.exercise_date is not None
        )

    def start_validity(self):
        return self._start_validity

    def end_validity(self):
        return self._end_validity

    def description(self):
        if not self._instance_outside and self._event and self._exclude:
            return self._event.description
        return f"{self._instance_outside.type_by_possession} {self._instance_outside}"

    def info_deficiencia_info_cota(self):
        value = None
        if self.vinculo_tp_reg_trab() == 1:
            result = (
                self._instance_outside.pessoa_fisica.deficiencyinformation.quota
                if hasattr(
                    self._instance_outside.pessoa_fisica, "deficiencyinformation"
                )
                else None
            )
            value = "S" if result else "N"
        return value

    def vinculo_matricula(self):
        return str(self._instance_outside.matricula)

    def info_celetista_dt_adm(self):
        return None

    def info_celetista_tp_admissao(self):
        return None

    def info_celetista_ind_admissao(self):
        return None

    def info_celetista_tp_reg_jor(self):
        return None

    def info_celetista_nat_atividade(self):
        return None

    def info_celetista_dt_base(self):
        return None

    def info_celetista_cnpj_sind_categ_prof(self):
        return None

    def info_celetista_mat_anot_jud(self):
        return None

    def fgts_dt_opc_fgts(self):
        return None

    def trab_temporario_hip_leg(self):
        return None

    def trab_temporario_just_contr(self):
        return None

    def ide_estab_vinc_tp_insc(self):
        return None

    def ide_estab_vinc_nr_insc(self):
        return None

    def ide_trab_substituido_cpf_trab_subst(self):
        return None

    def aprend_ind_aprend(self):
        return None

    def aprend_cnpj_ent_qual(self):
        return None

    def aprend_tp_insc(self):
        return None

    def aprend_nr_insc(self):
        return None

    def aprend_cnpj_prat(self):
        return None

    def info_estatutario_tp_prov(self):
        return tpProv(self._instance_outside)

    def info_estatutario_dt_exercicio(self):
        if self._instance_outside.type_by_possession == "COE":
            return self._instance_outside.created_at.date()
        return self._instance_outside.exercise_date

    def info_estatutario_tp_plan_rp(self):
        ss = self.social_security_employee()
        return (
            ss.mass_segregation_plan
            if ss and ss.social_security_config.regime != 1
            else None
        )

    def info_contrato_cod_categ(self):
        return employee_cod_categ(self._instance_outside)

    def info_contrato_nm_cargo(self):
        job_position_chart = self._get_cargo()[1]
        return f"{job_position_chart.title}"[0:99] if job_position_chart else None

    def info_contrato_cbo_cargo(self):
        cbo = None
        _, job_position_chart, config_job_position = self._get_cargo()
        if job_position_chart and job_position_chart.cbo:
            cbo = f"{job_position_chart.cbo.codigo}"
        elif config_job_position and config_job_position.cbo:
            cbo = f"{config_job_position.cbo.codigo}"
        return cbo

    def info_contrato_dt_ingr_cargo(self):
        value = None
        possession = self._get_cargo()[0]
        if possession:
            if (
                self.vinculo_cad_ini() == "S"
                and possession.data_exercicio < self.initial_group_date()
            ) or (
                self.vinculo_cad_ini() == "N"
                and self.info_estatutario_tp_prov() in [5, 8, 10]
            ):
                value = possession.data_exercicio
        return value

    def info_contrato_nm_funcao(self):
        job_position_chart = self._get_funcao()[1]
        return f"{job_position_chart.title}"[0:99] if job_position_chart else None

    def info_contrato_cbo_funcao(self):
        cbo = None
        _, job_position_chart, config_job_position = self._get_funcao()
        if job_position_chart and job_position_chart.cbo:
            cbo = f"{job_position_chart.cbo.codigo}"
        elif config_job_position and config_job_position.cbo:
            cbo = f"{config_job_position.cbo.codigo}"
        return cbo

    def info_contrato_acum_cargo(self):
        possession, job_position_chart, config_job_position = self._get_cargo()
        value = "S" if job_position_chart and job_position_chart.accumulate else "N"
        return value

    def info_celetista_nr_proc_trab(self):
        return None

    def info_estatutario_ind_teto_rgps(self):
        value = None
        if self.vinculo_tp_reg_prev() == 2:
            value = "N"
        return value

    def _get_abono(self):
        """Este método retorna a data do início do abono permanência."""
        start_date = self.start_validity()
        if start_date < self.initial_group_date():
            start_date = self.initial_group_date() - relativedelta(days=1)
        epp = ExtraPaymentPeriod.objects.currents_in(
            range=NewDateRange(start_date, start_date)
        ).filter(
            employee=self._instance_outside,
            extra_payment__slug__startswith="ABONO-PERMANENCIA",
            value__gt=0,
        )
        return epp.last().decision_date if epp.exists() else None

    def info_estatutario_ind_abono_perm(self):
        value = None
        if self.vinculo_tp_reg_prev() == 2:
            value = "S" if self._get_abono() else "N"
        return value

    def info_estatutario_dt_ini_abono(self):
        if self.info_estatutario_ind_abono_perm() == "S":
            return self._get_abono()
        return None

    def trei_cap_cod_trei_cap(self):
        return None

    def sucessao_vinc_nr_insc(self):
        return None

    def cessao_dt_ini_cessao(self):
        if not self.desligamento_dt_deslig():
            config = get_current_config()
            cut_date = max(config.cut_off_date_s2231, self.initial_group_date())
            cession = (
                AfastamentoOutroOrgao.objects.filter(servidor=self._instance_outside)
                .not_canceled()
                .currents_in(
                    range=NewDateRange(
                        self.initial_group_date(), self.initial_group_date()
                    )
                )
                .exclude(data_inicio__gt=cut_date)
                .exclude(data_fim__lte=cut_date)
            )
            return cession.last().data_inicio if cession.exists() else None
        return None

    def remuneracao_vr_sal_fx(self):
        """Salário base do trabalhador, correspondente à parte fixa da remuneração.
        Validação: Se {undSalFixo} for igual a [7], preencher com 0 (zero)."""
        value = None
        if self.vinculo_tp_reg_trab() != 2:
            remuneration = (
                self._instance_outside.remunerationbase_set.of_period(
                    self.last_period()
                )
                or self._instance_outside.remunerationbase_set.lasts()
            )
            value = get_base_salary(remuneration, self._instance_outside)
        return value

    def remuneracao_und_sal_fixo(self):
        """Unidade de pagamento da parte fixa da remuneração, conforme opções
        abaixo:
          1 - Por Hora;
          2 - Por Dia;
          3 - Por Semana;
          4 - Por Quinzena;
          5 - Por Mês;
          6 - Por Tarefa;
          7 - Não aplicável - salário exclusivamente variável.
        Valores Válidos: 1, 2, 3, 4, 5, 6, 7."""
        value = None
        if self.vinculo_tp_reg_trab() != 2:
            VALID_LINKS = ("EF", "CM", "FC")
            remuneration = (
                self._instance_outside.remunerationbase_set.of_period(
                    self.last_period()
                )
                .filter(link__in=VALID_LINKS)
                .last()
                or self._instance_outside.remunerationbase_set.filter(
                    link__in=VALID_LINKS
                )
                .lasts()
                .last()
            )
            reference = ReferenciaSalario.objects.get(pk=remuneration.salary)
            value = reference.referencia_nivel2d.estrutura_salarial.salary_unit or None
        return value

    def remuneracao_dsc_sal_var(self):
        """Descrição do salário por tarefa ou variável e como este é calculado.
        Ex.: Comissões pagas no percentual de 10% sobre as vendas.
        Validação: Preenchimento obrigatório se {undSalFixo} for igual a [6, 7]."""
        return None

    def duracao_tp_contr(self):
        """Tipo de contrato de trabalho conforme opções abaixo:
          1 - Prazo indeterminado;
          2 - Prazo determinado;
          3 - Prazo determinado, vinculado à ocorrência de um fato.
        Valores Válidos: 1, 2, 3
        """
        return None

    def duracao_dt_term(self):
        """Data do TérminoValidação: O preenchimento é obrigatório se {tpContr}
        igual a [2]. Deve ser igual ou posterior à data de admissão do servidor."""
        return None

    def duracao_clau_assec(self):
        """Indicar se o contrato por prazo determinado contém cláusula assecuratória
        do direito recíproco de rescisão antes da data de seu término:
          S - Sim;
          N - Não.
        Validação: O preenchimento é obrigatório se {tpContr} = [2]. Não preencher
        se {tpContr} = [1].
        Valores Válidos: S, N."""
        return None

    def duracao_obj_det(self):
        """Indicação do objeto determinante da contratação por prazo determinado (obra,
        serviço, safra, etc.).
        Validação: O preenchimento é obrigatório e exclusivo se {tpContr} = [3]."""
        return None

    def local_trab_geral_tp_insc(self):
        """Preencher com o código correspondente ao tipo de inscrição, conforme tabela 5
        Valores Válidos: 1, 3, 4."""
        return self.configuration.ide_employer_tp_insc

    def local_trab_geral_nr_insc(self):
        """Informar o número de inscrição do contribuinte de acordo com o tipo de
        inscrição indicado no campo {tpInsc}.
        Validação: A inscrição informada deve ser compatível com {tpInsc} e
        constar na tabela S-1005."""
        return self.configuration.ide_employer_nr_insc

    def local_trab_geral_desc_comp(self):
        return None

    def hor_contratual_qtd_hrs_sem(self):
        """Quantidade média de horas relativas à jornada semanal do trabalhador.
        Validação: Deve ser preenchido se {codCateg} <> [111].Se preenchido,
        deve ser maior que zero."""
        return get_weekly_workload(self._instance_outside)

    def hor_contratual_tp_jornada(self):
        """Tipo da Jornada. Preencher com uma das opções:
          1 - Jornada com horário diário e folga fixos;
          2 - Jornada 12 x 36 (12 horas de trabalho seguidas de 36 horas
          ininterruptas de descanso);
          3 - Jornada com horário diário fixo e folga variável;
          9 - Demais tipos de jornada.
        Valores Válidos: 1, 2, 3, 9"""
        return 1 if get_weekly_workload(self._instance_outside) else None

    def hor_contratual_tmp_parc(self):
        """Preencher com o código relativo ao tipo de contrato em tempo parcial:
          0 - Não é contrato em tempo parcial;
          1 - Limitado a 25 horas semanais;
          2 - Limitado a 30 horas semanais;
          3 - Limitado a 26 horas semanais.
        Validação: O código [1] só é válido se {codCateg} = [104]. Os
        códigos [2, 3] não são válidos se {codCateg} = [104].
        Valores Válidos: 0, 1, 2, 3."""
        return 0 if get_weekly_workload(self._instance_outside) else None

    def hor_contratual_hor_noturno(self):
        """
        Informação obrigatória se codCateg for diferente de [111].
        """
        return None

    def hor_contratual_dsc_jorn(self):
        return None

    def horario(self):
        return []

    def alvara_judicial_nr_proc_jud(self):
        """Preencher com o número do processo judicial.
        Validação: Deve ser um número de processo judicial válido, existente
        na Tabela de Processos - S-1070."""
        return None

    def observacoes_observacao(self):
        return None

    def sucessao_vinc_matric_ant(self):
        """Matrícula do trabalhador no empregador anterior.
        Validação: O preenchimento é obrigatório se {cadIni} = [N]."""
        return None

    def sucessao_vinc_dt_transf(self):
        """Preencher com a data da transferência do empregado para o empregador
        declarante.
        Validação: Devem ser observadas as seguintes regras:
          a) Deve ser posterior à data de admissão do trabalhador;
          b) Se {cadIni} = [S], deve ser anterior à data de início da obrigatoriedade
          do empregador no eSocial;
          c) Se {cadIni} = [N], deve ser igual ou posterior à data de início da
        obrigatoriedade do empregador no eSocial."""
        return None

    def sucessao_vinc_observacao(self):
        return None

    def transf_dom_cpf_substituido(self):
        """Preencher com o número do CPF do representante anterior da unidade familiar.
        Validação: O CPF informado deve ter registro de desligamento do mesmo{cpfTrab},
        com campo {cpfSubstituto} preenchido com o CPF do declarante."""
        return None

    def transf_dom_matric_ant(self):
        """Matrícula do trabalhador no representante anterior da unidade familiar."""
        return None

    def transf_dom_dt_transf(self):
        """Data da transferência do vínculo ao novo representante da unidade familiar.
        Validação: Deve ser o dia imediatamente seguinte à data de desligamento
        no CPF substituído."""
        return None

    def mudanca_cpf_cpf_ant(self):
        """Preencher com o número do CPF antigo do trabalhador."""
        return None

    def mudanca_cpf_matric_ant(self):
        """Preencher com a matrícula anterior do trabalhador."""
        return None

    def mudanca_cpf_dt_alt_cpf(self):
        """Data de alteração do CPF."""
        return None

    def mudanca_cpf_observacao(self):
        """Observação."""
        return None

    def afastamento_dt_ini_afast(self):
        """Data de início do afastamento.
        Validação: Devem ser observadas as seguintes regras:
            a) Deve ser igual ou posterior à data de
            admissão/exercício do trabalhador;
            b) Se cadIni = [S], deve ser anterior à data de início da
            obrigatoriedade dos eventos não periódicos para o
            empregador;
            c) Se cadIni = [N], deve ser anterior à data da
            transferência ou alteração do CPF do empregado
            (sucessaoVinc/dtTransf, transfDom/dtTransf ou dtAltCPF).
            Não informar se tpAdmissao = [1] ou se tpProv for
            diferente de [5, 8, 10].
        """
        if not self.desligamento_dt_deslig():
            departure = self.departure_employee()
            if departure and departure.data_inicio < self.initial_group_date():
                return departure.data_inicio
        return None

    def afastamento_cod_mot_afast(self):
        """
        Preencher com o código do motivo de afastamento
        temporário.
        Validação: Deve ser um código válido e existente na
        Tabela 18, bem como compatível com o código de
        categoria do trabalhador, conforme Tabela 18. Se a
        natureza jurídica do declarante for Administração Pública
        (grupo [1]), não pode ser informado [14].
        """
        from esocial.extractors.s2230 import ini_afastamento_cod_mot_afast

        if self.afastamento_dt_ini_afast():
            return ini_afastamento_cod_mot_afast(self.departure_employee())
        return None

    def desligamento_dt_deslig(self):
        """Preencher com a data do último dia trabalhado para o respectivo vínculo
        Validação: Deve ser uma data igual ou posterior à data de admissão e
        anterior ao início da obrigatoriedade do eSocial para o empregador."""
        list_end_date = self._references_strong_end_date(
            start_validity=self.start_validity()
        )
        list_end_date = set(
            filter(lambda x: x and x < self.initial_group_date(), list_end_date)
        )
        return min(list_end_date) if list_end_date else None

    def departure_employee(self):
        if self.vinculo_cad_ini() == "S":
            start_date = self.initial_group_date()
            departures = (
                BaseLicencaAfastamento.objects.of_employee(self._instance_outside)
                .esocial(data=start_date)
                .not_canceled()
            )
            departures = (
                departures.exclude(data_inicio__gt=start_date)
                .exclude(data_fim__lte=start_date)
                .exclude(
                    Q(
                        servidor__type_by_possession__in=[
                            "EFE",
                            "ECM",
                            "EFC",
                            "MBR",
                            "MEL",
                            "MCM",
                            "MEC",
                            "MBR2",
                            "MEL2",
                            "MCM2",
                            "MEC2",
                            "CMS",
                            "REQ",
                            "RCM",
                            "RFC",
                            "CTR",
                        ]
                    )
                    & Q(tipo=TYPE_VACATION)
                )
            )
            # FIXME: TRANSFERÊNCIA OU ALTERÁÇÃO DE CPF NÃO ESTÁ PREVISTA
            return departures.last()
        return None


def tpProv(employee):
    """1 Nomeação em cargo efetivo;
    2 Nomeação em cargo em comissão;
    3 - Incorporação (militar);
    4 - Matrícula (militar);
    5 - Reinclusão (militar);
    6 - Diplomação;
    7 - Contratação por tempo determinado;
    8 - Remoção (em caso de alteração do órgão declarante);
    99 - Outros não relacionados acima.
    100 - não pertence a este arquivo"""
    map_type = {
        "EFE": 1,  # SERVIDOR EFETIVO *
        "ECM": 1,  # SERVIDOR EFETIVO E COMISSIONADO *
        "EFC": 1,  # SERVIDOR EFETIVO COM FUNÇÃO CONFIANÇA *
        "MBR": 1,  # MEMBRO *
        "MEL": 1,  # MEMBRO COM CARGO ELETIVO *
        "MCM": 1,  # MEMBRO COM CARGO COMISSIONADO *
        "MEC": 1,  # MEMBRO COM CARGO ELETIVO E COMISSIONADO
        "MBR2": 1,  # MEMBRO *
        "MEL2": 1,  # MEMBRO COM CARGO ELETIVO *
        "MCM2": 1,  # MEMBRO COM CARGO COMISSIONADO *
        "MEC2": 1,  # MEMBRO COM CARGO ELETIVO E COMISSIONADO
        "CMS": 2,  # SERVIDOR COMISSIONADO
        "CTR": 99,  # SERVIDOR CONTRATADO
    }
    return map_type.get(employee.type_by_possession, 100)


def has_workload(employee):
    return employee.workload().last() is None


def get_weekly_workload(employee):
    return None


def get_base_salary(remuneration_bases, employee, main="EF"):
    cm = remuneration_bases.filter(link="CM")
    base_cm = cm.aggregate(Sum("base_value"))["base_value__sum"] or 0.0
    grat_cm = cm.aggregate(Sum("base_gratification"))["base_gratification__sum"] or 0.0
    fc = (
        remuneration_bases.filter(link="FC").aggregate(Sum("base_gratification"))[
            "base_gratification__sum"
        ]
        or 0.0
    )
    el = (
        remuneration_bases.filter(link="EL").aggregate(Sum("base_gratification"))[
            "base_gratification__sum"
        ]
        or 0.0
    )
    ef = (
        remuneration_bases.filter(link=main).aggregate(Sum("base_value"))[
            "base_value__sum"
        ]
        or 0.0
    )
    base = ef if employee.tipo_servidor == main else base_cm
    if employee.tipo_servidor == main and cm.exists():
        base = base_cm if base_cm > ef else ef
    grat = Decimal(grat_cm) + Decimal(fc) + Decimal(el)
    return Decimal(base) + Decimal(grat)


def employee_cod_categ(employee, info=""):
    try:
        cod_categ = employee.category_esocial
        if cod_categ == 1 or employee.type_by_possession == "COE":
            cod_categ = int(
                ItemTable.objects.by_info_choicecv_table(
                    employee.type_by_possession, "1", info=info
                ).code
            )
        return cod_categ
    except Exception as err:
        log.exception(err)
        log.debug(f"{employee} => {employee.type_by_possession}")
        raise Exception("Não possui Categoria do eSocial!")


class S2200Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2200
    EXTRACTOR = S2200Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        query = Servidor.objects.by_type_possession(valid_types())
        if not kwargs.get("dependency", False):
            query = query.exclude(
                termination_date__isnull=False,
                termination_date__lt=cls.initial_group_date(),
            )
        return query

    def _filter_by_factory(self, query, registry_employee=None, registry_person=None):
        """Este método deve ser utilizado para filter em query.

        Args:
            registry_employee (int): a matrícula do servidor
            registry_person (str): o cpf da pessoa física

        Returns:
            query (queryset):"""
        if registry_employee:
            query = query.filter(matricula=registry_employee)
        return query

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        return instance_outside.exercise_date

    def _get_end_limit(self, instance_outside, start_limit=None, organizer=None):
        return instance_outside.termination_date

    def _next_day(self, instance_outside, date=None, organizer=None):
        """Retorna o primeiro dia do próximo mês, que é o próximo dia de análise."""
        return None

    def delete_not_send(self, oid=None, registry=None, registry_person=None):
        from esocial.models import S2299

        for event in S2299.objects.can_exclude().filter(registry_employee=registry):
            event.delete()
        super().delete_not_send(oid=oid, registry=registry)
