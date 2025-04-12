# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S1020Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S1020Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_lotacao_cod_lotacao(self):
        return ""

    def ide_lotacao_ini_valid(self):
        return ""

    def ide_lotacao_fim_valid(self):
        return ""

    def dados_lotacao_tp_lotacao(self):
        return ""

    def dados_lotacao_tp_insc(self):
        return ""

    def dados_lotacao_nr_insc(self):
        return ""

    def fpas_lotacao_fpas(self):
        return ""

    def fpas_lotacao_cod_tercs(self):
        return ""

    def fpas_lotacao_cod_tercs_susp(self):
        return ""

    def proc_jud_terceiro(self):
        return ""

    def proc_jud_terceiro_cod_terc(self):
        return ""

    def proc_jud_terceiro_nr_proc_jud(self):
        return ""

    def proc_jud_terceiro_cod_susp(self):
        return ""

    def info_empr_parcial_tp_insc_contrat(self):
        return ""

    def info_empr_parcial_nr_insc_contrat(self):
        return ""

    def info_empr_parcial_tp_insc_prop(self):
        return ""

    def info_empr_parcial_nr_insc_prop(self):
        return ""

    def dados_op_port_aliq_rat(self):
        return ""

    def dados_op_port_fap(self):
        return ""

    def nova_validade_ini_valid(self):
        return ""

    def nova_validade_fim_valid(self):
        return ""
