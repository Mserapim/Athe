# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S1070Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S1070Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_processo_tp_proc(self):
        return ""

    def ide_processo_nr_proc(self):
        return ""

    def ide_processo_ini_valid(self):
        return ""

    def ide_processo_fim_valid(self):
        return ""

    def dados_proc_ind_autoria(self):
        return ""

    def dados_proc_ind_mat_proc(self):
        return ""

    def dados_proc_observacao(self):
        return ""

    def dados_proc_jud_uf_vara(self):
        return ""

    def dados_proc_jud_cod_munic(self):
        return ""

    def dados_proc_jud_id_vara(self):
        return ""

    def info_susp(self):
        return ""

    def info_susp_cod_susp(self):
        return ""

    def info_susp_ind_susp(self):
        return ""

    def info_susp_dt_decisao(self):
        return ""

    def info_susp_ind_deposito(self):
        return ""

    def nova_validade_ini_valid(self):
        return ""

    def nova_validade_fim_valid(self):
        return ""
