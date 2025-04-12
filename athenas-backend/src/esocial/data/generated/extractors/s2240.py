# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2240Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2240Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_vinculo_cpf_trab(self):
        return ""

    def ide_vinculo_matricula(self):
        return ""

    def ide_vinculo_cod_categ(self):
        return ""

    def info_exp_risco_dt_ini_condicao(self):
        return ""

    def info_amb_local_amb(self):
        return ""

    def info_amb_dsc_setor(self):
        return ""

    def info_amb_tp_insc(self):
        return ""

    def info_amb_nr_insc(self):
        return ""

    def info_ativ_dsc_ativ_des(self):
        return ""

    def ag_noc_cod_ag_noc(self):
        return ""

    def ag_noc_dsc_ag_noc(self):
        return ""

    def ag_noc_tp_aval(self):
        return ""

    def ag_noc_int_conc(self):
        return ""

    def ag_noc_lim_tol(self):
        return ""

    def ag_noc_un_med(self):
        return ""

    def ag_noc_tec_medicao(self):
        return ""

    def epc_epi_utiliz_epc(self):
        return ""

    def epc_epi_efic_epc(self):
        return ""

    def epc_epi_utiliz_epi(self):
        return ""

    def epi_doc_aval(self):
        return ""

    def epi_dsc_epi(self):
        return ""

    def epi_efic_epi(self):
        return ""

    def epi_compl_med_protecao(self):
        return ""

    def epi_compl_cond_functo(self):
        return ""

    def epi_compl_uso_inint(self):
        return ""

    def epi_compl_prz_valid(self):
        return ""

    def epi_compl_periodic_troca(self):
        return ""

    def epi_compl_higienizacao(self):
        return ""

    def resp_reg_cpf_resp(self):
        return ""

    def resp_reg_ide_oc(self):
        return ""

    def resp_reg_dsc_oc(self):
        return ""

    def resp_reg_nr_oc(self):
        return ""

    def resp_reg_uf_oc(self):
        return ""

    def obs_obs_compl(self):
        return ""
