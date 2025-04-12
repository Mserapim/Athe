# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2418Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2418Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_beneficio_cpf_benef(self):
        return ""

    def ide_beneficio_nr_beneficio(self):
        return ""

    def info_reativ_dt_efet_reativ(self):
        return ""

    def info_reativ_dt_efeito(self):
        return ""
