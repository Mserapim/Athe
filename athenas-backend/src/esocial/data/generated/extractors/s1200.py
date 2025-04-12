# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S1200Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S1200Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_evento_ind_guia(self):
        return ""

    def ide_trabalhador_cpf_trab(self):
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

    def info_complem_nm_trab(self):
        return ""

    def info_complem_dt_nascto(self):
        return ""

    def sucessao_vinc_tp_insc(self):
        return ""

    def sucessao_vinc_nr_insc(self):
        return ""

    def sucessao_vinc_matric_ant(self):
        return ""

    def sucessao_vinc_dt_adm(self):
        return ""

    def sucessao_vinc_observacao(self):
        return ""

    def proc_jud_trab(self):
        return ""

    def proc_jud_trab_tp_trib(self):
        return ""

    def proc_jud_trab_nr_proc_jud(self):
        return ""

    def proc_jud_trab_cod_susp(self):
        return ""

    def info_interm_dia(self):
        return ""

    def dm_dev_ide_dm_dev(self):
        return ""

    def dm_dev_cod_categ(self):
        return ""

    def ide_estab_lot_tp_insc(self):
        return ""

    def ide_estab_lot_nr_insc(self):
        return ""

    def ide_estab_lot_cod_lotacao(self):
        return ""

    def ide_estab_lot_qtd_dias_av(self):
        return ""

    def remun_per_apur_matricula(self):
        return ""

    def remun_per_apur_ind_simples(self):
        return ""

    def itens_remun_cod_rubr(self):
        return ""

    def itens_remun_ide_tab_rubr(self):
        return ""

    def itens_remun_qtd_rubr(self):
        return ""

    def itens_remun_fator_rubr(self):
        return ""

    def itens_remun_vr_rubr(self):
        return ""

    def itens_remun_ind_apur_ir(self):
        return ""

    def info_ag_nocivo_grau_exp(self):
        return ""

    def ide_adc_dt_ac_conv(self):
        return ""

    def ide_adc_tp_ac_conv(self):
        return ""

    def ide_adc_dsc(self):
        return ""

    def ide_adc_remun_suc(self):
        return ""

    def ide_periodo_per_ref(self):
        return ""

    def ide_periodo_ide_estab_lot_tp_insc(self):
        return ""

    def ide_periodo_ide_estab_lot_nr_insc(self):
        return ""

    def ide_periodo_ide_estab_lot_cod_lotacao(self):
        return ""

    def remun_per_ant_matricula(self):
        return ""

    def remun_per_ant_ind_simples(self):
        return ""

    def remun_per_ant_itens_remun_cod_rubr(self):
        return ""

    def remun_per_ant_itens_remun_ide_tab_rubr(self):
        return ""

    def remun_per_ant_itens_remun_qtd_rubr(self):
        return ""

    def remun_per_ant_itens_remun_fator_rubr(self):
        return ""

    def remun_per_ant_itens_remun_vr_rubr(self):
        return ""

    def remun_per_ant_itens_remun_ind_apur_ir(self):
        return ""

    def remun_per_ant_info_ag_nocivo_grau_exp(self):
        return ""

    def info_compl_cont_cod_cbo(self):
        return ""

    def info_compl_cont_nat_atividade(self):
        return ""

    def info_compl_cont_qtd_dias_trab(self):
        return ""
