# -.- coding: utf-8 -.-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor
from esocial.models import HealthCertificate

log = getLogger(__name__)


class HealthCertificateExtractor(Extractor):

    EXTRACTED_CLASS = HealthCertificate

    # def __init__(self, instance_outside, extracted_event=None, **kwargs):
    #     super(HealthCertificateExtractor, self).__init__(instance_outside, extracted_event=None, **kwargs)

    # def pos_validate(self, **kwargs):
    #     last_event = self.extracted_class.objects.exclude(
    #         pk=self._extracted_event.pk
    #     ).filter(
    #         oid=self._instance_outside.pk
    #     ).order_by('created_at').last()
    #     log.debug('LAST EVENT: %s' % last_event)
    #     if last_event and last_event.equals_by_fields(self._extracted_event):
    #         log.debug('>>>>>>>>>> DELETING EXTRACTED EVENT :: EQUAL LAST')
    #         self._extracted_event.delete()
    #         self._extracted_event = last_event

    def validate_validity_fields(self):
        pass

    def info_atestado_cod_cid(self):
        """
        Obrigatório apenas para motivo = '01'
        """
        return self._instance_outside.cid

    def info_atestado_qtd_dias_afast(self):
        return info_atestado_qtd_dias_afast(self._instance_outside)

    def emitente_nm_emit(self):
        return emitente_nm_emit(self._instance_outside)

    def emitente_ide_oc(self):
        return emitente_ide_oc(self._instance_outside)

    def emitente_nr_oc(self):
        return emitente_nr_oc(self._instance_outside)

    def emitente_uf_oc(self):
        return emitente_uf_oc(self._instance_outside)


def info_atestado_qtd_dias_afast(self):
    return self._instance_outside.days_granted


def emitente_nm_emit(self):
    return self._instance_outside.healthcare_professional.pessoa_fisica


def emitente_ide_oc(self):
    value = None
    if (
        self._instance_outside.healthcare_professional
        and self._instance_outside.healthcare_professional.pessoa_fisica.professional_council
    ):
        value = 1
    return value


def emitente_nr_oc(self):
    value = None
    if (
        self._instance_outside.healthcare_professional
        and self._instance_outside.healthcare_professional.pessoa_fisica.professional_council
    ):
        value = self._instance_outside.healthcare_professional.pessoa_fisica.professional_council.numero[
            0:13
        ]
    return value


def emitente_uf_oc(self):
    value = None
    if (
        self._instance_outside.healthcare_professional
        and self._instance_outside.healthcare_professional.pessoa_fisica.professional_council
        and self._instance_outside.healthcare_professional.pessoa_fisica.professional_council.estado_expedicao
    ):
        value = (
            self._instance_outside.healthcare_professional.pessoa_fisica.professional_council.estado_expedicao.sigla
        )
    return value
