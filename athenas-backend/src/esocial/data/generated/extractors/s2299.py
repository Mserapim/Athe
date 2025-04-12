# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2299Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2299Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_evento_ind_guia(self):
        return ""

    def ide_vinculo_cpf_trab(self):
        return ""

    def ide_vinculo_matricula(self):
        return ""

    def info_deslig_mtv_deslig(self):
        return ""

    def info_deslig_dt_deslig(self):
        return ""

    def info_deslig_dt_av_prv(self):
        return ""

    def info_deslig_ind_pagto_api(self):
        return ""

    def info_deslig_dt_proj_fim_api(self):
        return ""

    def info_deslig_pens_alim(self):
        return ""

    def info_deslig_perc_aliment(self):
        return ""

    def info_deslig_vr_alim(self):
        return ""

    def info_deslig_nr_proc_trab(self):
        return ""

    def info_interm_dia(self):
        return ""

    def observacoes_observacao(self):
        return ""

    def sucessao_vinc_tp_insc(self):
        return ""

    def sucessao_vinc_nr_insc(self):
        return ""

    def transf_tit_cpf_substituto(self):
        return ""

    def transf_tit_dt_nascto(self):
        return ""

    def mudanca_cpf_novo_cpf(self):
        return ""

    def dm_dev_ide_dm_dev(self):
        return ""

    def ide_estab_lot_tp_insc(self):
        return ""

    def ide_estab_lot_nr_insc(self):
        return ""

    def ide_estab_lot_cod_lotacao(self):
        return ""

    def det_verbas_cod_rubr(self):
        return ""

    def det_verbas_ide_tab_rubr(self):
        return ""

    def det_verbas_qtd_rubr(self):
        return ""

    def det_verbas_fator_rubr(self):
        return ""

    def det_verbas_vr_rubr(self):
        return ""

    def det_verbas_ind_apur_ir(self):
        return ""

    def info_ag_nocivo_grau_exp(self):
        return ""

    def info_simples_ind_simples(self):
        return ""

    def ide_adc_dt_ac_conv(self):
        return ""

    def ide_adc_tp_ac_conv(self):
        return ""

    def ide_adc_dsc(self):
        return ""

    def ide_periodo_per_ref(self):
        return ""

    def ide_periodo_ide_estab_lot_tp_insc(self):
        return ""

    def ide_periodo_ide_estab_lot_nr_insc(self):
        return ""

    def ide_periodo_ide_estab_lot_cod_lotacao(self):
        return ""

    def ide_estab_lot_det_verbas_cod_rubr(self):
        return ""

    def ide_estab_lot_det_verbas_ide_tab_rubr(self):
        return ""

    def ide_estab_lot_det_verbas_qtd_rubr(self):
        return ""

    def ide_estab_lot_det_verbas_fator_rubr(self):
        return ""

    def ide_estab_lot_det_verbas_vr_rubr(self):
        return ""

    def ide_estab_lot_det_verbas_ind_apur_ir(self):
        return ""

    def ide_estab_lot_info_ag_nocivo_grau_exp(self):
        return ""

    def ide_estab_lot_info_simples_ind_simples(self):
        return ""

    def proc_jud_trab(self):
        return ""

    def proc_jud_trab_tp_trib(self):
        return ""

    def proc_jud_trab_nr_proc_jud(self):
        return ""

    def proc_jud_trab_cod_susp(self):
        return ""

    def info_mv_ind_mv(self):
        return ""

    def remun_outr_empr_tp_insc(self):
        return ""

    def remun_outr_empr_nr_insc(self):
        return ""

    def remun_outr_empr_cod_categ(self):
        return ""

    def remun_outr_empr_vlr_remun_oe(self):
        return ""

    def proc_cs_nr_proc_jud(self):
        return ""

    def quarentena_dt_fim_quar(self):
        return ""

    def consig_fgts_ins_consig(self):
        return ""

    def consig_fgts_nr_contr(self):
        return ""
