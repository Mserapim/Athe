# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2200Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2200Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def trabalhador_cpf_trab(self):
        return ""

    def trabalhador_nm_trab(self):
        return ""

    def trabalhador_sexo(self):
        return ""

    def trabalhador_raca_cor(self):
        return ""

    def trabalhador_est_civ(self):
        return ""

    def trabalhador_grau_instr(self):
        return ""

    def trabalhador_nm_soc(self):
        return ""

    def nascimento_dt_nascto(self):
        return ""

    def nascimento_pais_nascto(self):
        return ""

    def nascimento_pais_nac(self):
        return ""

    def brasil_tp_lograd(self):
        return ""

    def brasil_dsc_lograd(self):
        return ""

    def brasil_nr_lograd(self):
        return ""

    def brasil_complemento(self):
        return ""

    def brasil_bairro(self):
        return ""

    def brasil_cep(self):
        return ""

    def brasil_cod_munic(self):
        return ""

    def brasil_uf(self):
        return ""

    def exterior_pais_resid(self):
        return ""

    def exterior_dsc_lograd(self):
        return ""

    def exterior_nr_lograd(self):
        return ""

    def exterior_complemento(self):
        return ""

    def exterior_bairro(self):
        return ""

    def exterior_nm_cid(self):
        return ""

    def exterior_cod_postal(self):
        return ""

    def trab_imig_tmp_resid(self):
        return ""

    def trab_imig_cond_ing(self):
        return ""

    def info_deficiencia_def_fisica(self):
        return ""

    def info_deficiencia_def_visual(self):
        return ""

    def info_deficiencia_def_auditiva(self):
        return ""

    def info_deficiencia_def_mental(self):
        return ""

    def info_deficiencia_def_intelectual(self):
        return ""

    def info_deficiencia_reab_readap(self):
        return ""

    def info_deficiencia_info_cota(self):
        return ""

    def info_deficiencia_observacao(self):
        return ""

    def dependente(self):
        return ""

    def dependente_tp_dep(self):
        return ""

    def dependente_nm_dep(self):
        return ""

    def dependente_dt_nascto(self):
        return ""

    def dependente_cpf_dep(self):
        return ""

    def dependente_sexo_dep(self):
        return ""

    def dependente_dep_irrf(self):
        return ""

    def dependente_dep_sf(self):
        return ""

    def dependente_inc_trab(self):
        return ""

    def contato_fone_princ(self):
        return ""

    def contato_email_princ(self):
        return ""

    def vinculo_matricula(self):
        return ""

    def vinculo_tp_reg_trab(self):
        return ""

    def vinculo_tp_reg_prev(self):
        return ""

    def vinculo_cad_ini(self):
        return ""

    def info_celetista_dt_adm(self):
        return ""

    def info_celetista_tp_admissao(self):
        return ""

    def info_celetista_ind_admissao(self):
        return ""

    def info_celetista_nr_proc_trab(self):
        return ""

    def info_celetista_tp_reg_jor(self):
        return ""

    def info_celetista_nat_atividade(self):
        return ""

    def info_celetista_dt_base(self):
        return ""

    def info_celetista_cnpj_sind_categ_prof(self):
        return ""

    def fgts_dt_opc_fgts(self):
        return ""

    def trab_temporario_hip_leg(self):
        return ""

    def trab_temporario_just_contr(self):
        return ""

    def ide_estab_vinc_tp_insc(self):
        return ""

    def ide_estab_vinc_nr_insc(self):
        return ""

    def ide_trab_substituido_cpf_trab_subst(self):
        return ""

    def aprend_tp_insc(self):
        return ""

    def aprend_nr_insc(self):
        return ""

    def info_estatutario_tp_prov(self):
        return ""

    def info_estatutario_dt_exercicio(self):
        return ""

    def info_estatutario_tp_plan_rp(self):
        return ""

    def info_estatutario_ind_teto_rgps(self):
        return ""

    def info_estatutario_ind_abono_perm(self):
        return ""

    def info_estatutario_dt_ini_abono(self):
        return ""

    def info_contrato_nm_cargo(self):
        return ""

    def info_contrato_cbo_cargo(self):
        return ""

    def info_contrato_dt_ingr_cargo(self):
        return ""

    def info_contrato_nm_funcao(self):
        return ""

    def info_contrato_cbo_funcao(self):
        return ""

    def info_contrato_acum_cargo(self):
        return ""

    def info_contrato_cod_categ(self):
        return ""

    def remuneracao_vr_sal_fx(self):
        return ""

    def remuneracao_und_sal_fixo(self):
        return ""

    def remuneracao_dsc_sal_var(self):
        return ""

    def duracao_tp_contr(self):
        return ""

    def duracao_dt_term(self):
        return ""

    def duracao_clau_assec(self):
        return ""

    def duracao_obj_det(self):
        return ""

    def local_trab_geral_tp_insc(self):
        return ""

    def local_trab_geral_nr_insc(self):
        return ""

    def local_trab_geral_desc_comp(self):
        return ""

    def local_temp_dom_tp_lograd(self):
        return ""

    def local_temp_dom_dsc_lograd(self):
        return ""

    def local_temp_dom_nr_lograd(self):
        return ""

    def local_temp_dom_complemento(self):
        return ""

    def local_temp_dom_bairro(self):
        return ""

    def local_temp_dom_cep(self):
        return ""

    def local_temp_dom_cod_munic(self):
        return ""

    def local_temp_dom_uf(self):
        return ""

    def hor_contratual(self):
        return ""

    def hor_contratual_qtd_hrs_sem(self):
        return ""

    def hor_contratual_tp_jornada(self):
        return ""

    def hor_contratual_tmp_parc(self):
        return ""

    def hor_contratual_hor_noturno(self):
        return ""

    def hor_contratual_dsc_jorn(self):
        return ""

    def alvara_judicial_nr_proc_jud(self):
        return ""

    def observacoes_observacao(self):
        return ""

    def trei_cap_cod_trei_cap(self):
        return ""

    def sucessao_vinc_tp_insc(self):
        return ""

    def sucessao_vinc_nr_insc(self):
        return ""

    def sucessao_vinc_matric_ant(self):
        return ""

    def sucessao_vinc_dt_transf(self):
        return ""

    def sucessao_vinc_observacao(self):
        return ""

    def transf_dom_cpf_substituido(self):
        return ""

    def transf_dom_matric_ant(self):
        return ""

    def transf_dom_dt_transf(self):
        return ""

    def mudanca_cpf_cpf_ant(self):
        return ""

    def mudanca_cpf_matric_ant(self):
        return ""

    def mudanca_cpf_dt_alt_cpf(self):
        return ""

    def mudanca_cpf_observacao(self):
        return ""

    def afastamento_dt_ini_afast(self):
        return ""

    def afastamento_cod_mot_afast(self):
        return ""

    def desligamento_dt_deslig(self):
        return ""

    def cessao_dt_ini_cessao(self):
        return ""
