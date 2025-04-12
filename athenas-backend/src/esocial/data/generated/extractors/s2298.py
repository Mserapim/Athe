# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2298Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2298Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_vinculo_cpf_trab(self):
        return ""

    def ide_vinculo_matricula(self):
        return ""

    def info_reintegr_tp_reint(self):
        return ""

    def info_reintegr_nr_proc_jud(self):
        return ""

    def info_reintegr_nr_lei_anistia(self):
        return ""

    def info_reintegr_dt_efet_retorno(self):
        return ""

    def info_reintegr_dt_efeito(self):
        return ""
