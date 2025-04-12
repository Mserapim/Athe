# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S1000Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S1000Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_periodo_ini_valid(self):
        return ""

    def ide_periodo_fim_valid(self):
        return ""

    def info_cadastro_class_trib(self):
        return ""

    def info_cadastro_ind_coop(self):
        return ""

    def info_cadastro_ind_constr(self):
        return ""

    def info_cadastro_ind_des_folha(self):
        return ""

    def info_cadastro_ind_opc_cp(self):
        return ""

    def info_cadastro_ind_porte(self):
        return ""

    def info_cadastro_ind_opt_reg_eletron(self):
        return ""

    def info_cadastro_cnpj_efr(self):
        return ""

    def dados_isencao_ide_min_lei(self):
        return ""

    def dados_isencao_nr_certif(self):
        return ""

    def dados_isencao_dt_emis_certif(self):
        return ""

    def dados_isencao_dt_venc_certif(self):
        return ""

    def dados_isencao_nr_prot_renov(self):
        return ""

    def dados_isencao_dt_prot_renov(self):
        return ""

    def dados_isencao_dt_dou(self):
        return ""

    def dados_isencao_pag_dou(self):
        return ""

    def info_org_internacional_ind_acordo_isen_multa(self):
        return ""

    def nova_validade_ini_valid(self):
        return ""

    def nova_validade_fim_valid(self):
        return ""
