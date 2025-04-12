# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S5003Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S5003Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_evento_nr_rec_arq_base(self):
        return ""

    def ide_trabalhador_cpf_trab(self):
        return ""

    def info_fgts_dt_venc(self):
        return ""

    def ide_estab_tp_insc(self):
        return ""

    def ide_estab_nr_insc(self):
        return ""

    def ide_lotacao_cod_lotacao(self):
        return ""

    def ide_lotacao_tp_lotacao(self):
        return ""

    def ide_lotacao_tp_insc(self):
        return ""

    def ide_lotacao_nr_insc(self):
        return ""

    def info_trab_fgts_matricula(self):
        return ""

    def info_trab_fgts_cod_categ(self):
        return ""

    def info_trab_fgts_categ_orig(self):
        return ""

    def info_trab_fgts_tp_reg_trab(self):
        return ""

    def info_trab_fgts_remun_suc(self):
        return ""

    def info_trab_fgts_dt_deslig(self):
        return ""

    def info_trab_fgts_mtv_deslig(self):
        return ""

    def info_trab_fgts_dt_term(self):
        return ""

    def info_trab_fgts_mtv_deslig_tsv(self):
        return ""

    def sucessao_vinc_tp_insc(self):
        return ""

    def sucessao_vinc_nr_insc(self):
        return ""

    def sucessao_vinc_matric_ant(self):
        return ""

    def sucessao_vinc_dt_adm(self):
        return ""

    def base_per_apur_tp_valor(self):
        return ""

    def base_per_apur_ind_incid(self):
        return ""

    def base_per_apur_rem_fgts(self):
        return ""

    def base_per_apur_dps_fgts(self):
        return ""

    def det_rubr_susp_cod_rubr(self):
        return ""

    def det_rubr_susp_ide_tab_rubr(self):
        return ""

    def det_rubr_susp_vr_rubr(self):
        return ""

    def ide_processo_fgts(self):
        return ""

    def ide_processo_fgts_nr_proc(self):
        return ""

    def info_base_per_ant_e_per_ref(self):
        return ""

    def base_per_ant_e_tp_valor_e(self):
        return ""

    def base_per_ant_e_ind_incid_e(self):
        return ""

    def base_per_ant_e_rem_fgtse(self):
        return ""

    def base_per_ant_e_dps_fgtse(self):
        return ""

    def base_per_ant_e_det_rubr_susp_cod_rubr(self):
        return ""

    def base_per_ant_e_det_rubr_susp_ide_tab_rubr(self):
        return ""

    def base_per_ant_e_det_rubr_susp_vr_rubr(self):
        return ""

    def ide_processo_fgts(self):
        return ""

    def det_rubr_susp_ide_processo_fgts_nr_proc(self):
        return ""

    def proc_cs_nr_proc_jud(self):
        return ""
