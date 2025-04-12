# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2206Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2206Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_vinculo_cpf_trab(self):
        return ""

    def ide_vinculo_matricula(self):
        return ""

    def alt_contratual_dt_alteracao(self):
        return ""

    def alt_contratual_dt_ef(self):
        return ""

    def alt_contratual_dsc_alt(self):
        return ""

    def vinculo_tp_reg_prev(self):
        return ""

    def info_celetista_tp_reg_jor(self):
        return ""

    def info_celetista_nat_atividade(self):
        return ""

    def info_celetista_dt_base(self):
        return ""

    def info_celetista_cnpj_sind_categ_prof(self):
        return ""

    def trab_temporario_just_prorr(self):
        return ""

    def aprend_tp_insc(self):
        return ""

    def aprend_nr_insc(self):
        return ""

    def info_estatutario_tp_plan_rp(self):
        return ""

    def info_estatutario_ind_teto_rgps(self):
        return ""

    def info_estatutario_ind_abono_perm(self):
        return ""

    def info_contrato_nm_cargo(self):
        return ""

    def info_contrato_cbo_cargo(self):
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
