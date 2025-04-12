# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S1202Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S1202Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_trabalhador_cpf_trab(self):
        return ""

    def info_complem_nm_trab(self):
        return ""

    def info_complem_dt_nascto(self):
        return ""

    def sucessao_vinc_cnpj_orgao_ant(self):
        return ""

    def sucessao_vinc_matric_ant(self):
        return ""

    def sucessao_vinc_dt_exercicio(self):
        return ""

    def sucessao_vinc_observacao(self):
        return ""

    def dm_dev_ide_dm_dev(self):
        return ""

    def dm_dev_cod_categ(self):
        return ""

    def ide_estab_tp_insc(self):
        return ""

    def ide_estab_nr_insc(self):
        return ""

    def remun_per_apur_matricula(self):
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

    def info_per_ant_remun_org_suc(self):
        return ""

    def ide_periodo_per_ref(self):
        return ""

    def ide_periodo_ide_estab_tp_insc(self):
        return ""

    def ide_periodo_ide_estab_nr_insc(self):
        return ""

    def remun_per_ant_matricula(self):
        return ""

    def remun_per_ant_itens_remun_cod_rubr(self):
        return ""

    def remun_per_ant_itens_remun_ide_tab_rubr(self):
        return ""

    def remun_per_ant_itens_remun_qtd_rubr(self):
        return ""

    def remun_per_ant_itens_remun_fator_rubr(self):
        return ""

    def remun_per_ant_itens_remun_vr_rubr(self):
        return ""

    def remun_per_ant_itens_remun_ind_apur_ir(self):
        return ""
