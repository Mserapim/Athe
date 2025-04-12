# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S5002Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S5002Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_evento_nr_rec_arq_base(self):
        return ""

    def ide_trabalhador_cpf_benef(self):
        return ""

    def dm_dev_per_ref(self):
        return ""

    def dm_dev_ide_dm_dev(self):
        return ""

    def dm_dev_tp_pgto(self):
        return ""

    def dm_dev_dt_pgto(self):
        return ""

    def dm_dev_cod_categ(self):
        return ""

    def info_ir_tp_info_ir(self):
        return ""

    def info_ir_valor(self):
        return ""
