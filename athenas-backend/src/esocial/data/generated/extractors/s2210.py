# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class S2210Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get("clear", False)
        super(S2210Extractor, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls):
        pass

    def ide_vinculo_cpf_trab(self):
        return ""

    def ide_vinculo_matricula(self):
        return ""

    def ide_vinculo_cod_categ(self):
        return ""

    def cat_dt_acid(self):
        return ""

    def cat_tp_acid(self):
        return ""

    def cat_hr_acid(self):
        return ""

    def cat_hrs_trab_antes_acid(self):
        return ""

    def cat_tp_cat(self):
        return ""

    def cat_ind_cat_obito(self):
        return ""

    def cat_dt_obito(self):
        return ""

    def cat_ind_comun_policia(self):
        return ""

    def cat_cod_sit_geradora(self):
        return ""

    def cat_iniciat_cat(self):
        return ""

    def cat_obs_cat(self):
        return ""

    def local_acidente_tp_local(self):
        return ""

    def local_acidente_dsc_local(self):
        return ""

    def local_acidente_tp_lograd(self):
        return ""

    def local_acidente_dsc_lograd(self):
        return ""

    def local_acidente_nr_lograd(self):
        return ""

    def local_acidente_complemento(self):
        return ""

    def local_acidente_bairro(self):
        return ""

    def local_acidente_cep(self):
        return ""

    def local_acidente_cod_munic(self):
        return ""

    def local_acidente_uf(self):
        return ""

    def local_acidente_pais(self):
        return ""

    def local_acidente_cod_postal(self):
        return ""

    def ide_local_acid_tp_insc(self):
        return ""

    def ide_local_acid_nr_insc(self):
        return ""

    def parte_atingida_cod_parte_ating(self):
        return ""

    def parte_atingida_lateralidade(self):
        return ""

    def agente_causador_cod_agnt_causador(self):
        return ""

    def atestado_dt_atendimento(self):
        return ""

    def atestado_hr_atendimento(self):
        return ""

    def atestado_ind_internacao(self):
        return ""

    def atestado_dur_trat(self):
        return ""

    def atestado_ind_afast(self):
        return ""

    def atestado_dsc_lesao(self):
        return ""

    def atestado_dsc_comp_lesao(self):
        return ""

    def atestado_diag_provavel(self):
        return ""

    def atestado_cod_cid(self):
        return ""

    def atestado_observacao(self):
        return ""

    def emitente_nm_emit(self):
        return ""

    def emitente_ide_oc(self):
        return ""

    def emitente_nr_oc(self):
        return ""

    def emitente_uf_oc(self):
        return ""

    def cat_origem_nr_rec_cat_orig(self):
        return ""
