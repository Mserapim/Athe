# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2230Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2230Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_vinculo_cpf_trab(self):
        return ""

    def ide_vinculo_matricula(self):
        return ""

    def ide_vinculo_cod_categ(self):
        return ""

    def ini_afastamento_dt_ini_afast(self):
        return ""

    def ini_afastamento_cod_mot_afast(self):
        return ""

    def ini_afastamento_info_mesmo_mtv(self):
        return ""

    def ini_afastamento_tp_acid_transito(self):
        return ""

    def ini_afastamento_observacao(self):
        return ""

    def per_aquis_dt_inicio(self):
        return ""

    def per_aquis_dt_fim(self):
        return ""

    def info_cessao_cnpj_cess(self):
        return ""

    def info_cessao_inf_onus(self):
        return ""

    def info_mand_sind_cnpj_sind(self):
        return ""

    def info_mand_sind_inf_onus_remun(self):
        return ""

    def info_mand_elet_cnpj_mand_elet(self):
        return ""

    def info_mand_elet_ind_remun_cargo(self):
        return ""

    def info_retif_orig_retif(self):
        return ""

    def info_retif_tp_proc(self):
        return ""

    def info_retif_nr_proc(self):
        return ""

    def fim_afastamento_dt_term_afast(self):
        return ""
