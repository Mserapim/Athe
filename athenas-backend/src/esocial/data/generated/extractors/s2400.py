# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2400Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2400Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def beneficiario_cpf_benef(self):
        return ""

    def beneficiario_nm_benefic(self):
        return ""

    def beneficiario_dt_nascto(self):
        return ""

    def beneficiario_dt_inicio(self):
        return ""

    def beneficiario_sexo(self):
        return ""

    def beneficiario_raca_cor(self):
        return ""

    def beneficiario_est_civ(self):
        return ""

    def beneficiario_inc_fis_men(self):
        return ""

    def beneficiario_dt_inc_fis_men(self):
        return ""

    def brasil_tp_lograd(self):
        return ""

    def brasil_dsc_lograd(self):
        return ""

    def brasil_nr_lograd(self):
        return ""

    def brasil_complemento(self):
        return ""

    def brasil_bairro(self):
        return ""

    def brasil_cep(self):
        return ""

    def brasil_cod_munic(self):
        return ""

    def brasil_uf(self):
        return ""

    def exterior_pais_resid(self):
        return ""

    def exterior_dsc_lograd(self):
        return ""

    def exterior_nr_lograd(self):
        return ""

    def exterior_complemento(self):
        return ""

    def exterior_bairro(self):
        return ""

    def exterior_nm_cid(self):
        return ""

    def exterior_cod_postal(self):
        return ""

    def dependente(self):
        return ""

    def dependente_tp_dep(self):
        return ""

    def dependente_nm_dep(self):
        return ""

    def dependente_dt_nascto(self):
        return ""

    def dependente_cpf_dep(self):
        return ""

    def dependente_sexo_dep(self):
        return ""

    def dependente_dep_irrf(self):
        return ""

    def dependente_inc_fis_men(self):
        return ""
