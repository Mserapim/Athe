# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S5013Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S5013Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def info_fgts_nr_rec_arq_base(self):
        return ""

    def info_fgts_ind_exist_info(self):
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

    def base_per_apur_tp_valor(self):
        return ""

    def base_per_apur_ind_incid(self):
        return ""

    def base_per_apur_base_fgts(self):
        return ""

    def base_per_apur_vr_fgts(self):
        return ""

    def info_base_per_ant_e_per_ref(self):
        return ""

    def base_per_ant_e_tp_valor_e(self):
        return ""

    def base_per_ant_e_ind_incid_e(self):
        return ""

    def base_per_ant_e_base_fgtse(self):
        return ""

    def base_per_ant_e_vr_fgtse(self):
        return ""
