# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2190Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2190Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def info_reg_prelim_cpf_trab(self):
        return ""

    def info_reg_prelim_dt_nascto(self):
        return ""

    def info_reg_prelim_dt_adm(self):
        return ""

    def info_reg_prelim_matricula(self):
        return ""

    def info_reg_prelim_cod_categ(self):
        return ""

    def info_reg_prelim_nat_atividade(self):
        return ""

    def info_reg_ctps_cbo_cargo(self):
        return ""

    def info_reg_ctps_vr_sal_fx(self):
        return ""

    def info_reg_ctps_und_sal_fixo(self):
        return ""

    def info_reg_ctps_tp_contr(self):
        return ""

    def info_reg_ctps_dt_term(self):
        return ""
