# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S5001Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S5001Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_evento_nr_rec_arq_base(self):
        return ""

    def ide_trabalhador_cpf_trab(self):
        return ""

    def sucessao_vinc_tp_insc(self):
        return ""

    def sucessao_vinc_nr_insc(self):
        return ""

    def sucessao_vinc_matric_ant(self):
        return ""

    def sucessao_vinc_dt_adm(self):
        return ""

    def info_interm_dia(self):
        return ""

    def info_compl_cont_cod_cbo(self):
        return ""

    def info_compl_cont_nat_atividade(self):
        return ""

    def info_compl_cont_qtd_dias_trab(self):
        return ""

    def proc_jud_trab(self):
        return ""

    def proc_jud_trab_nr_proc_jud(self):
        return ""

    def proc_jud_trab_cod_susp(self):
        return ""

    def info_cp_calc_tp_cr(self):
        return ""

    def info_cp_calc_vr_cp_seg(self):
        return ""

    def info_cp_calc_vr_desc_seg(self):
        return ""

    def ide_estab_lot_tp_insc(self):
        return ""

    def ide_estab_lot_nr_insc(self):
        return ""

    def ide_estab_lot_cod_lotacao(self):
        return ""

    def info_categ_incid_matricula(self):
        return ""

    def info_categ_incid_cod_categ(self):
        return ""

    def info_categ_incid_ind_simples(self):
        return ""

    def info_base_cs_ind13(self):
        return ""

    def info_base_cs_tp_valor(self):
        return ""

    def info_base_cs_valor(self):
        return ""

    def calc_terc_tp_cr(self):
        return ""

    def calc_terc_vr_cs_seg_terc(self):
        return ""

    def calc_terc_vr_desc_terc(self):
        return ""

    def info_per_ref_per_ref(self):
        return ""

    def ide_adc_dt_ac_conv(self):
        return ""

    def ide_adc_tp_ac_conv(self):
        return ""

    def ide_adc_dsc(self):
        return ""

    def ide_adc_remun_suc(self):
        return ""

    def det_info_per_ref_ind13(self):
        return ""

    def det_info_per_ref_tp_vr_per_ref(self):
        return ""

    def det_info_per_ref_vr_per_ref(self):
        return ""
