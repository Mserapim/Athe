# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2231Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2231Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_vinculo_cpf_trab(self):
        return ""

    def ide_vinculo_matricula(self):
        return ""

    def ini_cessao_dt_ini_cessao(self):
        return ""

    def ini_cessao_cnpj_cess(self):
        return ""

    def ini_cessao_resp_remun(self):
        return ""

    def fim_cessao_dt_term_cessao(self):
        return ""
