# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S1270Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S1270Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_evento_ind_guia(self):
        return ""

    def remun_av_np_tp_insc(self):
        return ""

    def remun_av_np_nr_insc(self):
        return ""

    def remun_av_np_cod_lotacao(self):
        return ""

    def remun_av_np_vr_bc_cp00(self):
        return ""

    def remun_av_np_vr_bc_cp15(self):
        return ""

    def remun_av_np_vr_bc_cp20(self):
        return ""

    def remun_av_np_vr_bc_cp25(self):
        return ""

    def remun_av_np_vr_bc_cp13(self):
        return ""

    def remun_av_np_vr_bc_fgts(self):
        return ""

    def remun_av_np_vr_desc_cp(self):
        return ""
