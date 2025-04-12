# -.- coding: utf-8 -.-
from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from esocial.const import DIFF_VALIDITY_END, NOTHING_TODO
from esocial.extractors.registrationbaseworker import address
from esocial.extractors.s2200 import (
    S2200Extractor,
    S2200Factory,
    employee_cod_categ,
    get_base_salary,
)
from esocial.extractors.s1200 import S1200Extractor
from esocial.models import S2300, ItemTable
from rh.models import Servidor
from datetime import datetime

log = getLogger(__name__)

VALID_LINKS_REQUESTED = ("REQ", "RCM", "RFC", "REX", "COE")
VALID_LINKS_REQUESTED_EXCLUDE_COE = ("REQ", "RCM", "RFC", "REX")
VALID_LINKS_EST = ("EST", "RES")
DATA_CORTE_COE = datetime(2025, 3, 1).date()


class S2300Extractor(S2200Extractor):
    """
    O evento S-2300 é permitido apenas para as categorias de
    trabalhadores [201, 202, 304, 305, 308, 311, 313, 401, 410,
    501, 701, 711, 712, 721, 722, 723, 731, 734, 738, 741, 751,
    761, 771, 781, 901, 902, 903, 904].
    """

    VALIDITY_FIELDS = ["info_tsv_inicio_dt_inicio"]

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

    def _references_strong_start_date(self):
        if self._instance_outside.type_by_possession == "COE":
            return [self._instance_outside.created_at.date()]
        return [self._instance_outside.exercise_date]

    @classmethod
    def _termination_date(cls, instance_outside, start_validity=None):
        termination_date = None
        if termination_date and termination_date < cls.initial_group_date():
            termination_date = instance_outside.termination_date
        return termination_date

    def _query_config_reference(self):
        """Este método retorna o queryset da referência. Definido

        Returns:
            queryset
        """
        date_reference = self._instance_outside.exercise_date
        if self._instance_outside.type_by_possession == "COE":
            date_reference = self._instance_outside.created_at.date()

        if self._start_validity:
            query = self._config().assets_in(
                range=NewDateRange(date_reference, date_reference)
            )
        else:
            query = self._class_config.objects.none()
        return query

    def _config(self):
        """Este método retorna o queryset básico da referência.

        Returns:
            queryset
        """
        return self._instance_outside.posses.filter(
            Q(quadro__cargo__tipo_lei_cargo__in=["CM", "FC"])
            | Q(
                servidor__type_by_possession__in=VALID_LINKS_REQUESTED + VALID_LINKS_EST
            )
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
                .assets_in(range=NewDateRange(start_date, end_date))
                .exclude(quadro__cargo__tipo_lei_cargo__in=["CM", "FC"])
                .last()
            )
            if possession:
                if possession.quadro:
                    config_job_position = possession.quadro.cargo.get_configs(
                        start_date=start_date, end_date=end_date
                    ).last()
                    return (
                        possession.my_origin,
                        possession.quadro.job_position_chart,
                        config_job_position,
                    )
                else:
                    return possession.my_origin, None, None
        return None, None, None

    def request_move(self):
        if not hasattr(self, "_request_move"):
            possession, _, _ = self._get_cargo()
            if possession.my_type == "requestmove":
                setattr(self, "_request_move", possession)
        return getattr(self, "_request_move", None)

    def possession_trainee(self):
        if not hasattr(self, "_possession_trainee"):
            possession, _, _ = self._get_cargo()
            if possession.my_type == "possessiontrainee":
                setattr(self, "_possession_trainee", possession)
            # if possession.my_type == 'possessionresident':
            #     setattr(self, '_possession_trainee', possession)
        return getattr(self, "_possession_trainee", None)

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
        if self._instance_outside.type_by_possession == "COE":
            return self._instance_outside.created_at.date()
        return (
            self._instance_outside and self._instance_outside.exercise_date is not None
        )

    def description(self):
        if not self._instance_outside and self._event and self._exclude:
            return self._event.description
        return f"{self._instance_outside.type_by_possession} {self._instance_outside}"

    @property
    def trainee(self):
        return self._instance_outside.type_by_possession in VALID_LINKS_EST

    @property
    def requested(self):
        return (
            self._instance_outside.type_by_possession
            in VALID_LINKS_REQUESTED_EXCLUDE_COE
        )

    def info_tsv_inicio_cad_ini(self):
        """Indicar se o evento se refere a cadastramento inicial (o ingresso do trabalhador no empregador declarante é anterior à data
        de início da obrigatoriedade de envio de seus eventos não periódicos) ou se refere a um início de TSVE
        (o ingresso do trabalhador no empregador declarante é igual ou posterior à data de início da obrigatoriedade de envio de seus
        eventos não periódicos):
            S - Sim (Cadastramento Inicial);
            N - Não (Início de TSVE).
        Valores Válidos: S, N."""
        return self.vinculo_cad_ini()

    def info_tsv_inicio_matricula(self):
        return self.vinculo_matricula()

    def info_tsv_inicio_cod_categ(self):
        """Preencher com o código da categoria do trabalhador, conforme Tabela 1.
        Validação: Deve existir na Tabela de Categorias de Trabalhadores (tabela 1)."""
        return employee_cod_categ(self._instance_outside)

    def info_tsv_inicio_dt_inicio(self):
        """Data de início, que pode ser:
          a) Para o Cooperado, a data de ingresso na cooperativa;
          b) Para o Diretor Não Empregado, a data de posse no cargo;
          c) Para o Dirigente Sindical, a data de início do mandato no sindicato;
          d) Para o Estagiário, a data de início do estágio;
          e) Para o trabalhador avulso, a data de ingresso no ogmo ou no Sindicato;
          f) Para os demais trabalhadores, a data de início das atividades no empregador.
        Validação: Devem ser observadas as seguintes regras:
          a) Deve ser posterior à data de nascimento do trabalhador;.
          b) Se {cadIni} = [S], deve ser anterior à data de início da obrigatoriedade dos eventos não periódicos para o empregador no
            eSocial;
          c) Se {cadIni} = [N], deve ser igual ou posterior à data de início da obrigatoriedade dos eventos não periódicos para o
            empregador no eSocial."""
        return self.info_estatutario_dt_exercicio()

    def info_tsv_inicio_nr_proc_trab(self):
        return None

    def info_tsv_inicio_nat_atividade(self):
        """Natureza da atividade, conforme opções abaixo:
          1 - Trabalho Urbano;
          2 - Trabalho Rural.
        Validação: Preenchimento obrigatório para as categorias de avulso, cooperado e dirigente sindical. Não deve ser preenchido
        para as categorias Diretor não empregado, servidor público indicado a conselho, membro de conselho tutelar e estagiário.
        Valores Válidos: 1, 2."""
        return None

    def remuneracao_vr_sal_fx(self):
        """Salário base do trabalhador, correspondente à parte fixa da remuneração.
        Validação: Se {undSalFixo} for igual a [7], preencher com 0 (zero)."""
        remuneration = (
            self._instance_outside.remunerationbase_set.of_period(self.last_period())
            or self._instance_outside.remunerationbase_set.lasts()
        )
        return get_base_salary(remuneration, self._instance_outside, "AC")

    def remuneracao_und_sal_fixo(self):
        """Unidade de pagamento da parte fixa da remuneração, conforme opções abaixo:
          1 - Por Hora;
          2 - Por Dia;
          3 - Por Semana;
          4 - Por Quinzena;
          5 - Por Mês;
          6 - Por Tarefa;
          7 - Não aplicável - salário exclusivamente variável.
        Valores Válidos: 1, 2, 3, 4, 5, 6, 7."""
        return 5

    def fgts_dt_opc_fgts(self):
        """Informar a data de opção do trabalhador pelo FGTS. Validação: Preenchimento obrigatório em caso de trabalhador optante pelo
        FGTS."""
        return None

    def info_dirigente_sindical_categ_orig(self):
        """Preencher com o código correspondente à categoria de origem do dirigente sindical.
        Validação: Deve ser uma categoria diferente de "Dirigente Sindical"."""
        return None

    def info_dirigente_sindical_tp_insc(self):
        return None

    def info_dirigente_sindical_nr_insc(self):
        return None

    def info_dirigente_sindical_dt_adm_orig(self):
        """Preencher com a data de admissão ou data de início do dirigente sindical na empresa de origem.
        Validação: O preenchimento é obrigatório se a categoria de origem do trabalhador corresponder a "empregado" ou "avulso".
        """
        return None

    def info_dirigente_sindical_matric_orig(self):
        """Preencher com a matrícula do trabalhador na empresa de origem.
        Validação: Preenchimento obrigatório se a categoria de origem do trabalhador corresponder a "empregado".
        """
        return None

    def info_dirigente_sindical_tp_reg_trab(self):
        return None

    def info_dirigente_sindical_tp_reg_prev(self):
        return None

    def info_mand_elet_ind_remun_cargo(self):
        return None

    def info_mand_elet_tp_reg_trab(self):
        return None

    def info_mand_elet_tp_reg_prev(self):
        return None

    def mudanca_cpf_cpf_ant(self):
        """Preencher com o número do CPF antigo do trabalhador."""
        return None

    def mudanca_cpf_matric_ant(self):
        return None

    def mudanca_cpf_dt_alt_cpf(self):
        """Data de alteração do CPF."""
        return None

    def mudanca_cpf_observacao(self):
        """Observação."""
        return None

    def termino_dt_term(self):
        """Preencher com a data do término. Validação: Devem ser observadas as seguintes regras:
        a) Deve ser igual ou posterior à data de início do TSVE;
        b) Deve ser anterior à data de início da obrigatoriedade dos eventos não periódicos para o empregador.
        """
        return self.desligamento_dt_deslig()

    def cargo_funcao_nm_cargo(self):
        """Informar o nome do cargo. Validação: Preenchimento obrigatório se codCateg for diferente de [410]."""
        if self.info_tsv_inicio_cod_categ() in (901, 903, 904):
            return None

        if self._instance_outside.type_by_possession == "COE":
            cbo = info_cbo_cargo_prestador_servico(self._instance_outside.pessoa_fisica)
            return cbo.descricao

        nm_cargo = None
        _, job_position_chart, config_job_position = self._get_cargo()
        if job_position_chart:
            nm_cargo = f"{job_position_chart.title}"
        elif config_job_position:
            nm_cargo = f"{config_job_position.job_position}"
        return nm_cargo[0:99] if nm_cargo else nm_cargo

    def cargo_funcao_cbo_cargo(self):
        """Informar o nome do cargo. Validação: Preenchimento obrigatório se codCateg for diferente de [410]."""
        if self.info_tsv_inicio_cod_categ() in (901, 903, 904):
            return None

        if self._instance_outside.type_by_possession == "COE":
            cbo = info_cbo_cargo_prestador_servico(self._instance_outside.pessoa_fisica)
            return cbo.codigo

        cbo = None
        _, job_position_chart, config_job_position = self._get_cargo()
        if job_position_chart and job_position_chart.cbo:
            cbo = f"{job_position_chart.cbo.codigo}"
        elif config_job_position and config_job_position.cbo:
            cbo = f"{config_job_position.cbo.codigo}"
        return cbo

    def cargo_funcao_nm_funcao(self):
        """Preencher com o nome da função, se utilizado pelo empregador."""
        if self.info_tsv_inicio_cod_categ() in (901, 903, 904):
            return None

        nm_funcao = None
        if self.requested:
            nm_funcao = self.info_contrato_nm_funcao()
        return nm_funcao

    def cargo_funcao_cbo_funcao(self):
        if self.info_tsv_inicio_cod_categ() in (901, 903, 904):
            return None

        cbo = None
        if self.requested:
            cbo = self.info_contrato_cbo_funcao()
        return cbo

    def info_trab_cedido_categ_orig(self):
        """Preencher com o código correspondente à categoria de origem do trabalhador cedido."""
        if self.requested:
            if not self.request_move():
                print(f"{self._instance_outside} não possui Requisição.")
                print(self._instance_outside)
                print(self._start_validity)
            else:
                return (
                    301
                    if not self.request_move().category
                    else self.request_move().category
                )
        return None

    def info_trab_cedido_cnpj_cednt(self):
        """Informar o CNPJ da empresa cedente.
        Validação: Deve ser um CNPJ válido, com raiz diferente da empresa declarante.
        Regra de validação: REGRA_VALIDA_CNPJ."""
        if self.requested:
            if (
                self.request_move()
                and not self.request_move().organ_origin.pessoa_juridica
            ):
                print(
                    f"{self.request_move()} não possui pessoa jurídica em {self.request_move().organ_origin}"
                )
            else:
                return self.request_move().organ_origin.pessoa_juridica.cnpj
        return None

    def info_trab_cedido_matric_ced(self):
        """Preencher com a matrícula do trabalhador no empregador de origem (Cedente)."""
        if self.requested:
            return str(
                self._instance_outside.matricula_origem
                or self._instance_outside.matricula
            )
        return None

    def info_trab_cedido_dt_adm_ced(self):
        """Preencher com a data de admissão do trabalhador no empregador de origem (Cedente).
        Validação: Deve ser uma data anterior a data de início informada no evento."""
        if self.requested:
            return (
                self.request_move().possession_origin_date
                if self.request_move()
                else None
            )
        return None

    def info_trab_cedido_tp_reg_trab(self):
        """Tipo de regime trabalhista
        1 - CLT - Consolidação das Leis de Trabalho e legislações trabalhistas específicas;
        2 - Estatutário. Valores Válidos: 1, 2."""
        if self.requested and self.request_move():
            return self.request_move().regime_contract
        return None

    def info_trab_cedido_tp_reg_prev(self):
        """Tipo de regime previdenciário conforme opções abaixo:
          1 - Regime Geral da Previdência Social - RGPS;
          2 - Regime Próprio de Previdência Social - RPPS;
          3 - Regime de Previdência Social no Exterior.
        Validação: Se {categOrig} for relativa a Empregado, não pode ser preenchido com [2].
        Valores Válidos: 1, 2, 3."""
        if self.requested:
            return self.vinculo_tp_reg_prev()
        return None

    def info_mand_elet_categ_orig(self):
        return None

    def info_mand_elet_cnpj_orig(self):
        return None

    def info_mand_elet_matric_orig(self):
        return None

    def info_mand_elet_dt_exerc_orig(self):
        return None

    """ESTAGIÁRIO"""

    def info_estagiario_nat_estagio(self):
        """Natureza do Estágio:
          O - Obrigatório;
          N - Não Obrigatório.
        Valores Válidos: O, N."""
        if self.trainee and self.possession_trainee():
            if (
                self.possession_trainee().nature
                and self.possession_trainee().nature == 1
            ):
                return "O"
            else:
                return "N"
        return None

    def info_estagiario_niv_estagio(self):
        """Informar o nível do estágio:
          1 - Fundamental;
          2 - Médio;
          3 - Formação Profissional;
          4 - Superior;
          8 - Especial;
          9 - Mãe social. (Lei 7644, de 1987).
        Valores Válidos: 1, 2, 3, 4, 8, 9."""
        if self.trainee and self.possession_trainee():
            return (
                self.possession_trainee().level if self.possession_trainee() else None
            )
        return None

    def info_estagiario_area_atuacao(self):
        if self.trainee and self.possession_trainee():
            return (
                self.possession_trainee().occupation_area or None
                if self.possession_trainee()
                else None
            )
        return None

    def info_estagiario_nr_apol(self):
        """Nr. Apólice de Seguro. Preencher com o valor da bolsa, se o estágio for remunerado."""
        if self.trainee and self.possession_trainee():
            return (
                self.possession_trainee().insurance_number or None
                if self.possession_trainee()
                else None
            )
        return None

    def info_estagiario_dt_prev_term(self):
        """Data prevista para o término do estágio. Validação: Deve ser uma data posterior à data de início do estágio."""
        if self.trainee and self.possession_trainee():
            return (
                self._instance_outside.termination_date
                if self._instance_outside
                else None
            )
        return None

    def inst_ensino_cnpj_inst_ensino(self):
        """Preencher com o cnpj da instituição de ensino. Deve ser preenchido apenas se a instituição de ensino for brasileira."""
        if self.trainee and self.possession_trainee():
            if self.possession_trainee().educational_institution:
                return self.possession_trainee().educational_institution.cnpj
        return None

    def inst_ensino_nm_razao(self):
        """Informar a razão social."""
        if self.trainee and not self.inst_ensino_cnpj_inst_ensino():
            if self.possession_trainee().educational_institution:
                return self.possession_trainee().educational_institution.razao_social
        return None

    def inst_ensino_dsc_lograd(self):
        """Descrição do logradouro."""
        if self.trainee and not self.inst_ensino_cnpj_inst_ensino():
            ad = get_address_ie(self.possession_trainee().educational_institution)
            return ad.logradouro[:100] if ad else None
        return None

    def inst_ensino_nr_lograd(self):
        """Número do logradouro."""
        if self.trainee and not self.inst_ensino_cnpj_inst_ensino():
            ad = get_address_ie(self.possession_trainee().educational_institution)
            return ad.numero[:10] or "S/N" if ad else None
        return None

    def inst_ensino_bairro(self):
        """Nome do bairro/distrito."""
        if self.trainee and not self.inst_ensino_cnpj_inst_ensino():
            ad = get_address_ie(self.possession_trainee().educational_institution)
            return ad.bairro[:90] if ad else None
        return None

    def inst_ensino_cep(self):
        """Código de Endereçamento Postal - CEP.
        Validação: Deve ser preenchido apenas com números.
        Deve ser um CEP válido."""
        if self.trainee and not self.inst_ensino_cnpj_inst_ensino():
            ad = get_address_ie(self.possession_trainee().educational_institution)
            return ("".join(filter(str.isdigit, str(ad.cep)))[0:8]) if ad else None
        return None

    def inst_ensino_cod_munic(self):
        """Preencher com o código do município, conforme tabela do IBGE.
        Validação: Se informado, deve ser um código existente na tabela do IBGE."""
        if self.trainee and not self.inst_ensino_cnpj_inst_ensino():
            ad = get_address_ie(self.possession_trainee().educational_institution)
            return ad.municipio.ibge if ad else None
        return None

    def inst_ensino_uf(self):
        """Preencher com a sigla da Unidade da Federação. Validação: Deve ser uma UF válida."""
        if self.trainee and not self.inst_ensino_cnpj_inst_ensino():
            ad = get_address_ie(self.possession_trainee().educational_institution)
            return ad.municipio.estado.sigla if ad else None
        return None

    def age_integracao_cnpj_agnt_integ(self):
        """CNPJ do agente de integração. Validação: Deve ser um CNPJ válido. Regra de validação: REGRA_VALIDA_CNPJ."""
        if self.trainee and self.possession_trainee():
            if self.possession_trainee().integration_agent:
                return self.possession_trainee().integration_agent.cnpj
        return None

    def supervisor_estagio_cpf_supervisor(self):
        """CPF do responsável pela supervisão do estagiário. Validação: Deve ser um CPF válido. Nome do Supervisor do Estágio."""
        if self.trainee and self.possession_trainee():
            if (
                self.possession_trainee()
                and self.possession_trainee().employee_supervisor
            ):
                return self.possession_trainee().employee_supervisor.pessoa_fisica.cpf
        return None

    def local_trab_geral_tp_insc(self):
        if self._instance_outside.type_by_possession == "COE":
            return None

        if self.trainee:
            if self.possession_trainee():
                return self.configuration.ide_employer_tp_insc
            else:
                return None
        return self.configuration.ide_employer_tp_insc

    def local_trab_geral_nr_insc(self):
        if self._instance_outside.type_by_possession == "COE":
            return None

        if self.trainee:
            if self.possession_trainee():
                return self.configuration.ide_employer_nr_insc
            else:
                return None
        return self.configuration.ide_employer_nr_insc

    def local_trab_geral_desc_comp(self):
        return None


def info_cbo_cargo_prestador_servico(pessoa_fisica):
    prestador_servico = pessoa_fisica.pf_providers.last()
    if prestador_servico:
        return prestador_servico.cbo
    return None


def get_address_ie(inst_ens):
    return address(inst_ens) if inst_ens else inst_ens


class S2300Factory(S2200Factory):

    EXTRACTED_MODEL_CLASS = S2300
    EXTRACTOR = S2300Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        query = Servidor.objects.by_type_possession(
            VALID_LINKS_REQUESTED + VALID_LINKS_EST
        ).exclude(
            Q(type_by_possession="COE"),
            Q(pessoa_fisica__modified_at__date__lt=DATA_CORTE_COE)
            | Q(pessoa_fisica__pf_providers__isnull=True),
        )

        if not kwargs.get("dependency", False):
            query = query.exclude(
                termination_date__isnull=False,
                termination_date__lt=cls.initial_group_date(),
            )
        return query

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        if instance_outside.type_by_possession == "COE":
            return instance_outside.created_at.date()
        return instance_outside.exercise_date

    def delete_not_send(self, oid=None, registry=None, registry_person=None):
        from esocial.models import S2399

        for event in S2399.objects.can_exclude().filter(registry_employee=registry):
            event.delete()
        super().delete_not_send(oid=oid, registry=registry)
