# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2205Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2205Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_trabalhador_cpf_trab(self):
        return ""

    def alteracao_dt_alteracao(self):
        return ""

    def dados_trabalhador_nm_trab(self):
        return ""

    def dados_trabalhador_sexo(self):
        return ""

    def dados_trabalhador_raca_cor(self):
        return ""

    def dados_trabalhador_est_civ(self):
        return ""

    def dados_trabalhador_grau_instr(self):
        return ""

    def dados_trabalhador_nm_soc(self):
        return ""

    def dados_trabalhador_pais_nac(self):
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

    def trab_imig_tmp_resid(self):
        return ""

    def trab_imig_cond_ing(self):
        return ""

    def info_deficiencia_def_fisica(self):
        return ""

    def info_deficiencia_def_visual(self):
        return ""

    def info_deficiencia_def_auditiva(self):
        return ""

    def info_deficiencia_def_mental(self):
        return ""

    def info_deficiencia_def_intelectual(self):
        return ""

    def info_deficiencia_reab_readap(self):
        return ""

    def info_deficiencia_info_cota(self):
        return ""

    def info_deficiencia_observacao(self):
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

    def dependente_dep_sf(self):
        return ""

    def dependente_inc_trab(self):
        return ""

    def contato_fone_princ(self):
        return ""

    def contato_email_princ(self):
        return ""
