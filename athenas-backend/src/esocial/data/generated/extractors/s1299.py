# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S1299Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S1299Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_evento_ind_guia(self):
        return ""

    def info_fech_evt_remun(self):
        return ""

    def info_fech_evt_com_prod(self):
        return ""

    def info_fech_evt_contrat_av_np(self):
        return ""

    def info_fech_evt_info_compl_per(self):
        return ""
