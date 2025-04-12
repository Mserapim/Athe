# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2416Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2416Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_beneficio_cpf_benef(self):
        return ""

    def ide_beneficio_nr_beneficio(self):
        return ""

    def info_ben_alteracao_dt_alt_beneficio(self):
        return ""

    def dados_beneficio_tp_beneficio(self):
        return ""

    def dados_beneficio_tp_plan_rp(self):
        return ""

    def dados_beneficio_dsc(self):
        return ""

    def dados_beneficio_ind_suspensao(self):
        return ""

    def info_pen_morte_tp_pen_morte(self):
        return ""

    def suspensao_mtv_suspensao(self):
        return ""

    def suspensao_dsc_suspensao(self):
        return ""
