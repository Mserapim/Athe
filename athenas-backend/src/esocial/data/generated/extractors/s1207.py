# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S1207Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S1207Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_benef_cpf_benef(self):
        return ""

    def dm_dev_ide_dm_dev(self):
        return ""

    def dm_dev_nr_beneficio(self):
        return ""

    def ide_estab_tp_insc(self):
        return ""

    def ide_estab_nr_insc(self):
        return ""

    def itens_remun_cod_rubr(self):
        return ""

    def itens_remun_ide_tab_rubr(self):
        return ""

    def itens_remun_qtd_rubr(self):
        return ""

    def itens_remun_fator_rubr(self):
        return ""

    def itens_remun_vr_rubr(self):
        return ""

    def itens_remun_ind_apur_ir(self):
        return ""

    def ide_periodo_per_ref(self):
        return ""

    def ide_periodo_ide_estab_tp_insc(self):
        return ""

    def ide_periodo_ide_estab_nr_insc(self):
        return ""

    def ide_estab_itens_remun_cod_rubr(self):
        return ""

    def ide_estab_itens_remun_ide_tab_rubr(self):
        return ""

    def ide_estab_itens_remun_qtd_rubr(self):
        return ""

    def ide_estab_itens_remun_fator_rubr(self):
        return ""

    def ide_estab_itens_remun_vr_rubr(self):
        return ""

    def ide_estab_itens_remun_ind_apur_ir(self):
        return ""
