# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S3000Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S3000Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def info_exclusao_tp_evento(self):
        return ""

    def info_exclusao_nr_rec_evt(self):
        return ""

    def ide_trabalhador_cpf_trab(self):
        return ""
