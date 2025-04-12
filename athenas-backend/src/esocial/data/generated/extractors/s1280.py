# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S1280Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S1280Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_evento_ind_guia(self):
        return ""

    def info_subst_patr_ind_subst_patr(self):
        return ""

    def info_subst_patr_perc_red_contrib(self):
        return ""

    def info_subst_patr_op_port_cod_lotacao(self):
        return ""

    def info_ativ_concom_fator_mes(self):
        return ""

    def info_ativ_concom_fator13(self):
        return ""
