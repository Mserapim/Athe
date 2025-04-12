# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2410Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2410Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def beneficiario_cpf_benef(self):
        return ""

    def beneficiario_matricula(self):
        return ""

    def beneficiario_cnpj_origem(self):
        return ""

    def info_ben_inicio_cad_ini(self):
        return ""

    def info_ben_inicio_ind_sit_benef(self):
        return ""

    def info_ben_inicio_nr_beneficio(self):
        return ""

    def info_ben_inicio_dt_ini_beneficio(self):
        return ""

    def info_ben_inicio_dt_public(self):
        return ""

    def dados_beneficio_tp_beneficio(self):
        return ""

    def dados_beneficio_tp_plan_rp(self):
        return ""

    def dados_beneficio_dsc(self):
        return ""

    def dados_beneficio_ind_dec_jud(self):
        return ""

    def info_pen_morte_tp_pen_morte(self):
        return ""

    def inst_pen_morte_cpf_inst(self):
        return ""

    def inst_pen_morte_dt_inst(self):
        return ""

    def sucessao_benef_cnpj_orgao_ant(self):
        return ""

    def sucessao_benef_nr_beneficio_ant(self):
        return ""

    def sucessao_benef_dt_transf(self):
        return ""

    def sucessao_benef_observacao(self):
        return ""

    def mudanca_cpf_cpf_ant(self):
        return ""

    def mudanca_cpf_nr_beneficio_ant(self):
        return ""

    def mudanca_cpf_dt_alt_cpf(self):
        return ""

    def mudanca_cpf_observacao(self):
        return ""

    def info_ben_termino_dt_term_beneficio(self):
        return ""

    def info_ben_termino_mtv_termino(self):
        return ""
