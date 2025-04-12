# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2300Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2300Extractor, self).__init__(*args, **kwargs)

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

    def info_tsv_inicio_cad_ini(self):
        return ""

    def info_tsv_inicio_matricula(self):
        return ""

    def info_tsv_inicio_cod_categ(self):
        return ""

    def info_tsv_inicio_dt_inicio(self):
        return ""

    def info_tsv_inicio_nr_proc_trab(self):
        return ""

    def info_tsv_inicio_nat_atividade(self):
        return ""

    def cargo_funcao_nm_cargo(self):
        return ""

    def cargo_funcao_cbo_cargo(self):
        return ""

    def cargo_funcao_nm_funcao(self):
        return ""

    def cargo_funcao_cbo_funcao(self):
        return ""

    def remuneracao_vr_sal_fx(self):
        return ""

    def remuneracao_und_sal_fixo(self):
        return ""

    def remuneracao_dsc_sal_var(self):
        return ""

    def fgts_dt_opc_fgts(self):
        return ""

    def info_dirigente_sindical_categ_orig(self):
        return ""

    def info_dirigente_sindical_tp_insc(self):
        return ""

    def info_dirigente_sindical_nr_insc(self):
        return ""

    def info_dirigente_sindical_dt_adm_orig(self):
        return ""

    def info_dirigente_sindical_matric_orig(self):
        return ""

    def info_dirigente_sindical_tp_reg_trab(self):
        return ""

    def info_dirigente_sindical_tp_reg_prev(self):
        return ""

    def info_trab_cedido_categ_orig(self):
        return ""

    def info_trab_cedido_cnpj_cednt(self):
        return ""

    def info_trab_cedido_matric_ced(self):
        return ""

    def info_trab_cedido_dt_adm_ced(self):
        return ""

    def info_trab_cedido_tp_reg_trab(self):
        return ""

    def info_trab_cedido_tp_reg_prev(self):
        return ""

    def info_mand_elet_ind_remun_cargo(self):
        return ""

    def info_mand_elet_tp_reg_trab(self):
        return ""

    def info_mand_elet_tp_reg_prev(self):
        return ""

    def info_estagiario_nat_estagio(self):
        return ""

    def info_estagiario_niv_estagio(self):
        return ""

    def info_estagiario_area_atuacao(self):
        return ""

    def info_estagiario_nr_apol(self):
        return ""

    def info_estagiario_dt_prev_term(self):
        return ""

    def inst_ensino_cnpj_inst_ensino(self):
        return ""

    def inst_ensino_nm_razao(self):
        return ""

    def inst_ensino_dsc_lograd(self):
        return ""

    def inst_ensino_nr_lograd(self):
        return ""

    def inst_ensino_bairro(self):
        return ""

    def inst_ensino_cep(self):
        return ""

    def inst_ensino_cod_munic(self):
        return ""

    def inst_ensino_uf(self):
        return ""

    def age_integracao_cnpj_agnt_integ(self):
        return ""

    def supervisor_estagio_cpf_supervisor(self):
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

    def termino_dt_term(self):
        return ""
