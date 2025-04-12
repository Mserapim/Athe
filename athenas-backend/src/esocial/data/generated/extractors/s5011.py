# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S5011Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S5011Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def info_cs_nr_rec_arq_base(self):
        return ""

    def info_cs_ind_exist_info(self):
        return ""

    def info_cp_seg_vr_desc_cp(self):
        return ""

    def info_cp_seg_vr_cp_seg(self):
        return ""

    def info_contrib_class_trib(self):
        return ""

    def info_pj_ind_coop(self):
        return ""

    def info_pj_ind_constr(self):
        return ""

    def info_pj_ind_subst_patr(self):
        return ""

    def info_pj_perc_red_contrib(self):
        return ""

    def info_at_conc_fator_mes(self):
        return ""

    def info_at_conc_fator13(self):
        return ""

    def ide_estab_tp_insc(self):
        return ""

    def ide_estab_nr_insc(self):
        return ""

    def info_estab_cnae_prep(self):
        return ""

    def info_estab_aliq_rat(self):
        return ""

    def info_estab_fap(self):
        return ""

    def info_estab_aliq_rat_ajust(self):
        return ""

    def info_compl_obra_ind_subst_patr_obra(self):
        return ""

    def ide_lotacao_cod_lotacao(self):
        return ""

    def ide_lotacao_fpas(self):
        return ""

    def ide_lotacao_cod_tercs(self):
        return ""

    def ide_lotacao_cod_tercs_susp(self):
        return ""

    def info_terc_susp_cod_terc(self):
        return ""

    def info_empr_parcial_tp_insc_contrat(self):
        return ""

    def info_empr_parcial_nr_insc_contrat(self):
        return ""

    def info_empr_parcial_tp_insc_prop(self):
        return ""

    def info_empr_parcial_nr_insc_prop(self):
        return ""

    def info_empr_parcial_cno_obra(self):
        return ""

    def dados_op_port_cnpj_op_portuario(self):
        return ""

    def dados_op_port_aliq_rat(self):
        return ""

    def dados_op_port_fap(self):
        return ""

    def dados_op_port_aliq_rat_ajust(self):
        return ""

    def bases_remun_ind_incid(self):
        return ""

    def bases_remun_cod_categ(self):
        return ""

    def bases_cp_vr_bc_cp00(self):
        return ""

    def bases_cp_vr_bc_cp15(self):
        return ""

    def bases_cp_vr_bc_cp20(self):
        return ""

    def bases_cp_vr_bc_cp25(self):
        return ""

    def bases_cp_vr_susp_bc_cp00(self):
        return ""

    def bases_cp_vr_susp_bc_cp15(self):
        return ""

    def bases_cp_vr_susp_bc_cp20(self):
        return ""

    def bases_cp_vr_susp_bc_cp25(self):
        return ""

    def bases_cp_vr_bc_cp00_va(self):
        return ""

    def bases_cp_vr_bc_cp15_va(self):
        return ""

    def bases_cp_vr_bc_cp20_va(self):
        return ""

    def bases_cp_vr_bc_cp25_va(self):
        return ""

    def bases_cp_vr_susp_bc_cp00_va(self):
        return ""

    def bases_cp_vr_susp_bc_cp15_va(self):
        return ""

    def bases_cp_vr_susp_bc_cp20_va(self):
        return ""

    def bases_cp_vr_susp_bc_cp25_va(self):
        return ""

    def bases_cp_vr_desc_sest(self):
        return ""

    def bases_cp_vr_calc_sest(self):
        return ""

    def bases_cp_vr_desc_senat(self):
        return ""

    def bases_cp_vr_calc_senat(self):
        return ""

    def bases_cp_vr_sal_fam(self):
        return ""

    def bases_cp_vr_sal_mat(self):
        return ""

    def bases_av_n_port_vr_bc_cp00(self):
        return ""

    def bases_av_n_port_vr_bc_cp15(self):
        return ""

    def bases_av_n_port_vr_bc_cp20(self):
        return ""

    def bases_av_n_port_vr_bc_cp25(self):
        return ""

    def bases_av_n_port_vr_bc_cp13(self):
        return ""

    def bases_av_n_port_vr_desc_cp(self):
        return ""

    def info_subst_patr_op_port_cnpj_op_portuario(self):
        return ""

    def bases_comerc_ind_comerc(self):
        return ""

    def bases_comerc_vr_bc_com_pr(self):
        return ""

    def bases_comerc_vr_cp_susp(self):
        return ""

    def bases_comerc_vr_rat_susp(self):
        return ""

    def bases_comerc_vr_senar_susp(self):
        return ""

    def info_cr_estab_tp_cr(self):
        return ""

    def info_cr_estab_vr_cr(self):
        return ""

    def info_cr_estab_vr_susp_cr(self):
        return ""

    def info_cr_contrib(self):
        return ""

    def tp_cr(self):
        return ""

    def vr_cr(self):
        return ""

    def vr_cr_susp(self):
        return ""
