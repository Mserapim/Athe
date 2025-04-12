# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S1005Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S1005Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_estab_tp_insc(self):
        return ""

    def ide_estab_nr_insc(self):
        return ""

    def ide_estab_ini_valid(self):
        return ""

    def ide_estab_fim_valid(self):
        return ""

    def dados_estab_cnae_prep(self):
        return ""

    def aliq_gilrat_aliq_rat(self):
        return ""

    def aliq_gilrat_fap(self):
        return ""

    def proc_adm_jud_rat_tp_proc(self):
        return ""

    def proc_adm_jud_rat_nr_proc(self):
        return ""

    def proc_adm_jud_rat_cod_susp(self):
        return ""

    def proc_adm_jud_fap_tp_proc(self):
        return ""

    def proc_adm_jud_fap_nr_proc(self):
        return ""

    def proc_adm_jud_fap_cod_susp(self):
        return ""

    def info_caepf_tp_caepf(self):
        return ""

    def info_obra_ind_subst_patr_obra(self):
        return ""

    def info_apr_nr_proc_jud(self):
        return ""

    def info_ent_educ_nr_insc(self):
        return ""

    def info_pcd_nr_proc_jud(self):
        return ""

    def nova_validade_ini_valid(self):
        return ""

    def nova_validade_fim_valid(self):
        return ""
