# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S1010Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S1010Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_rubrica_cod_rubr(self):
        return ""

    def ide_rubrica_ide_tab_rubr(self):
        return ""

    def ide_rubrica_ini_valid(self):
        return ""

    def ide_rubrica_fim_valid(self):
        return ""

    def dados_rubrica_dsc_rubr(self):
        return ""

    def dados_rubrica_nat_rubr(self):
        return ""

    def dados_rubrica_tp_rubr(self):
        return ""

    def dados_rubrica_cod_inc_cp(self):
        return ""

    def dados_rubrica_cod_inc_irrf(self):
        return ""

    def dados_rubrica_cod_inc_fgts(self):
        return ""

    def dados_rubrica_cod_inc_cprp(self):
        return ""

    def dados_rubrica_teto_remun(self):
        return ""

    def dados_rubrica_observacao(self):
        return ""

    def ide_processo_cp(self):
        return ""

    def ide_processo_cp_tp_proc(self):
        return ""

    def ide_processo_cp_nr_proc(self):
        return ""

    def ide_processo_cp_ext_decisao(self):
        return ""

    def ide_processo_cp_cod_susp(self):
        return ""

    def ide_processo_irrf(self):
        return ""

    def ide_processo_irrf_nr_proc(self):
        return ""

    def ide_processo_irrf_cod_susp(self):
        return ""

    def ide_processo_fgts(self):
        return ""

    def ide_processo_fgts_nr_proc(self):
        return ""

    def nova_validade_ini_valid(self):
        return ""

    def nova_validade_fim_valid(self):
        return ""
