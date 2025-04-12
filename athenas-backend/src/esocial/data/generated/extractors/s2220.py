# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2220Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2220Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_vinculo_cpf_trab(self):
        return ""

    def ide_vinculo_matricula(self):
        return ""

    def ide_vinculo_cod_categ(self):
        return ""

    def ex_med_ocup_tp_exame_ocup(self):
        return ""

    def aso_dt_aso(self):
        return ""

    def aso_res_aso(self):
        return ""

    def exame_dt_exm(self):
        return ""

    def exame_proc_realizado(self):
        return ""

    def exame_obs_proc(self):
        return ""

    def exame_ord_exame(self):
        return ""

    def exame_ind_result(self):
        return ""

    def medico_nm_med(self):
        return ""

    def medico_nr_crm(self):
        return ""

    def medico_uf_crm(self):
        return ""

    def resp_monit_cpf_resp(self):
        return ""

    def resp_monit_nm_resp(self):
        return ""

    def resp_monit_nr_crm(self):
        return ""

    def resp_monit_uf_crm(self):
        return ""
