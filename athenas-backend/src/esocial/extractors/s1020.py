# -.- coding: utf-8 -.-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor, Factory, administrative_unit
from esocial.models import S1020
from rh.models import TaxAllocationConfig, UnidadeAdministrativa

from .utils import format_reference, limits_from_date

log = getLogger(__name__)


class S1020Extractor(Extractor):

    VALIDITY_FIELDS = [
        "ide_lotacao_ini_valid",
        "ide_lotacao_fim_valid",
        "nova_validade_ini_valid",
        "nova_validade_fim_valid",
    ]

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
        return TaxAllocationConfig

    def _config(self):
        return self._class_config.objects.filter(
            administrative_unit__pk=self._instance_outside.pk
        )

    def ide_lotacao_cod_lotacao(self):
        return self._instance_outside.pessoa_juridica.cnpj

    def ide_lotacao_ini_valid(self):
        if self._event:
            return format_reference(self._event.start_validity)
        return super(S1020Extractor, self).ini_valid()

    def ide_lotacao_fim_valid(self):
        if self._event:
            return format_reference(self._event.end_validity)
        return super(S1020Extractor, self).fim_valid()

    def dados_lotacao_tp_lotacao(self):
        return "01"

    def dados_lotacao_tp_insc(self):
        return None

    def dados_lotacao_nr_insc(self):
        return None

    def fpas_lotacao_fpas(self):
        config = self._query_config_reference().last()
        return config.fpas if config else None

    def fpas_lotacao_cod_tercs(self):
        config = self._query_config_reference().last()
        return config.terc_code if config else None

    def fpas_lotacao_cod_tercs_susp(self):
        return None

    def proc_jud_terceiro(self):
        suspensions = []
        return suspensions

    def info_empr_parcial_tp_insc_contrat(self):
        return None

    def info_empr_parcial_nr_insc_contrat(self):
        return None

    def info_empr_parcial_tp_insc_prop(self):
        return None

    def info_empr_parcial_nr_insc_prop(self):
        return None

    def dados_op_port_aliq_rat(self):
        return None

    def dados_op_port_fap(self):
        return None

    def nova_validade_ini_valid(self):
        return super(S1020Extractor, self).ini_valid()

    def nova_validade_fim_valid(self):
        return super(S1020Extractor, self).fim_valid()


class S1020Factory(Factory):

    EXTRACTED_MODEL_CLASS = S1020
    EXTRACTOR = S1020Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        return UnidadeAdministrativa.objects.filter(pk=administrative_unit().pk)
