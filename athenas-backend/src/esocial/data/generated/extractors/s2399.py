# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2399Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2399Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_evento_ind_guia(self):
        return ""

    def ide_trab_sem_vinculo_cpf_trab(self):
        return ""

    def ide_trab_sem_vinculo_matricula(self):
        return ""

    def ide_trab_sem_vinculo_cod_categ(self):
        return ""

    def info_tsv_termino_dt_term(self):
        return ""

    def info_tsv_termino_mtv_deslig_tsv(self):
        return ""

    def info_tsv_termino_pens_alim(self):
        return ""

    def info_tsv_termino_perc_aliment(self):
        return ""

    def info_tsv_termino_vr_alim(self):
        return ""

    def info_tsv_termino_nr_proc_trab(self):
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

    def info_simples_ind_simples(self):
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

    def quarentena_dt_fim_quar(self):
        return ""
