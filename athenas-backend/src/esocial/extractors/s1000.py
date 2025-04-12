# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.const import DIFF_VALIDITY_END_SAME_CONTENT
from esocial.extractors.base import Extractor, Factory, administrative_unit
from esocial.models import S1000
from rh.models import AdministrativeUnitConfig, UnidadeAdministrativa

from .utils import format_reference, limits_from_date

log = getLogger(__name__)


class S1000Extractor(Extractor):

    VALIDITY_FIELDS = [
        "ide_periodo_ini_valid",
        "ide_periodo_fim_valid",
        "nova_validade_ini_valid",
        "nova_validade_fim_valid",
    ]

    def __init__(self, *args, **kwargs):
        super(S1000Extractor, self).__init__(*args, **kwargs)

    def _references(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return self._references_strong() + self._references_weak()

    def _references_strong(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        references = []
        q_config_reference = self._query_config_reference()
        if q_config_reference.exists():
            references.append(q_config_reference.last())
        return references

    def _references_strong_start_date(self):
        return [
            limits_from_date(obj.start_validity)[0] for obj in self._references_strong()
        ]

    def _references_end_date(self):
        return [obj.end_validity for obj in self._references() if obj.end_validity]

    @property
    def _class_config(self):
        return AdministrativeUnitConfig

    def _config(self):
        return self._class_config.objects.filter(
            administrative_unit__pk=self._instance_outside.pk
        )

    def _run_event_modification(self, validate=None, **kwargs):
        """GERANDO Event de alteração"""
        if validate != DIFF_VALIDITY_END_SAME_CONTENT:
            super()._run_event_modification(validate=validate, **kwargs)

    def ide_periodo_ini_valid(self):
        if self._event:
            return format_reference(self._event.start_validity)
        return super(S1000Extractor, self).ini_valid()

    def ide_periodo_fim_valid(self):
        if self._event:
            return format_reference(self._event.end_validity)
        return super(S1000Extractor, self).fim_valid()

    def info_cadastro_class_trib(self):
        config = self._query_config_reference().last()
        value = str("{:2d}".format(config.tax_classification))
        if self.clear:
            return "00"
        else:
            return value

    def info_cadastro_ind_coop(self):
        return 0

    def info_cadastro_ind_constr(self):
        return 0

    def info_cadastro_ind_des_folha(self):
        return 0

    def info_cadastro_ind_opc_cp(self):
        return None

    def info_cadastro_ind_porte(self):
        return None

    def info_cadastro_ind_opt_reg_eletron(self):
        config = self._query_config_reference().last()
        return 1 if config and config.eletronic_reg_employees else 0

    def info_cadastro_cnpj_efr(self):
        config = self._query_config_reference().last()
        return (
            config.federative_body.cnpj if config and config.federative_body else None
        )

    def dados_isencao_ide_min_lei(self):
        return None

    def dados_isencao_nr_certif(self):
        return None

    def dados_isencao_dt_emis_certif(self):
        return None

    def dados_isencao_dt_venc_certif(self):
        return None

    def dados_isencao_nr_prot_renov(self):
        return None

    def dados_isencao_dt_prot_renov(self):
        return None

    def dados_isencao_dt_dou(self):
        return None

    def dados_isencao_pag_dou(self):
        return None

    def info_org_internacional_ind_acordo_isen_multa(self):
        return None

    def nova_validade_ini_valid(self):
        return super(S1000Extractor, self).ini_valid()

    def nova_validade_fim_valid(self):
        return super(S1000Extractor, self).fim_valid()


class S1000Factory(Factory):

    EXTRACTED_MODEL_CLASS = S1000
    EXTRACTOR = S1000Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        return UnidadeAdministrativa.objects.filter(pk=administrative_unit().pk)
