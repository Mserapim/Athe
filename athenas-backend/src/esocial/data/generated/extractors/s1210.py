# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S1210Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S1210Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_evento_ind_guia(self):
        return ""

    def ide_benef_cpf_benef(self):
        return ""

    def info_pgto_dt_pgto(self):
        return ""

    def info_pgto_tp_pgto(self):
        return ""

    def info_pgto_per_ref(self):
        return ""

    def info_pgto_ide_dm_dev(self):
        return ""

    def info_pgto_vr_liq(self):
        return ""
