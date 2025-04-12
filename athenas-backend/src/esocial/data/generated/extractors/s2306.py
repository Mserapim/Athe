# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2306Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2306Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_trab_sem_vinculo_cpf_trab(self):
        return ""

    def ide_trab_sem_vinculo_matricula(self):
        return ""

    def ide_trab_sem_vinculo_cod_categ(self):
        return ""

    def info_tsv_alteracao_dt_alteracao(self):
        return ""

    def info_tsv_alteracao_nat_atividade(self):
        return ""

    def cargo_funcao_nm_cargo(self):
        return ""

    def cargo_funcao_cbo_cargo(self):
        return ""

    def cargo_funcao_nm_funcao(self):
        return ""

    def cargo_funcao_cbo_funcao(self):
        return ""

    def remuneracao_vr_sal_fx(self):
        return ""

    def remuneracao_und_sal_fixo(self):
        return ""

    def remuneracao_dsc_sal_var(self):
        return ""

    def info_dirigente_sindical_tp_reg_prev(self):
        return ""

    def info_trab_cedido_tp_reg_prev(self):
        return ""

    def info_mand_elet_ind_remun_cargo(self):
        return ""

    def info_mand_elet_tp_reg_prev(self):
        return ""

    def info_estagiario_nat_estagio(self):
        return ""

    def info_estagiario_niv_estagio(self):
        return ""

    def info_estagiario_area_atuacao(self):
        return ""

    def info_estagiario_nr_apol(self):
        return ""

    def info_estagiario_dt_prev_term(self):
        return ""

    def inst_ensino_cnpj_inst_ensino(self):
        return ""

    def inst_ensino_nm_razao(self):
        return ""

    def inst_ensino_dsc_lograd(self):
        return ""

    def inst_ensino_nr_lograd(self):
        return ""

    def inst_ensino_bairro(self):
        return ""

    def inst_ensino_cep(self):
        return ""

    def inst_ensino_cod_munic(self):
        return ""

    def inst_ensino_uf(self):
        return ""

    def age_integracao_cnpj_agnt_integ(self):
        return ""

    def supervisor_estagio_cpf_supervisor(self):
        return ""
