# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from rh.afastamento.api.baselicencaafastamento import AFABaseLicencaAfastamentoRestful
from rh.afastamento.models import (
    Licenca,
    LicencaAfastamentoConjuge,
    LicencaAtividadePolitica,
    LicencaCapacitacao,
    LicencaInteresseParticular,
    LicencaMandatoClassista,
    LicencaServicoMilitar,
    AwardLicense,
)

log = getLogger(__name__)


class AFALicencaRestful(AFABaseLicencaAfastamentoRestful):

    full_text_index = () + AFABaseLicencaAfastamentoRestful.full_text_index

    exclude_fields = [] + AFABaseLicencaAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFABaseLicencaAfastamentoRestful.force_persist_boolean_fields
    )

    _model = Licenca

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.licenca.Manage")')


class AFALicencaAfastamentoConjugeRestful(AFALicencaRestful):

    full_text_index = () + AFALicencaRestful.full_text_index

    exclude_fields = [] + AFALicencaRestful.exclude_fields

    force_persist_boolean_fields = [] + AFALicencaRestful.force_persist_boolean_fields

    _model = LicencaAfastamentoConjuge

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.licencaafastamentoconjuge.Manage")'
        )


class AFALicencaAtividadePoliticaRestful(AFALicencaRestful):

    full_text_index = () + AFALicencaRestful.full_text_index

    exclude_fields = [] + AFALicencaRestful.exclude_fields

    force_persist_boolean_fields = [] + AFALicencaRestful.force_persist_boolean_fields

    _model = LicencaAtividadePolitica

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.licencaatividadepolitica.Manage")'
        )


class AFALicencaCapacitacaoRestful(AFALicencaRestful):

    full_text_index = () + AFALicencaRestful.full_text_index

    exclude_fields = [] + AFALicencaRestful.exclude_fields

    force_persist_boolean_fields = [] + AFALicencaRestful.force_persist_boolean_fields

    _model = LicencaCapacitacao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.licencacapacitacao.Manage")')


class AFALicencaInteresseParticularRestful(AFALicencaRestful):

    full_text_index = () + AFALicencaRestful.full_text_index

    exclude_fields = [] + AFALicencaRestful.exclude_fields

    force_persist_boolean_fields = [] + AFALicencaRestful.force_persist_boolean_fields

    _model = LicencaInteresseParticular

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.licencainteresseparticular.Manage")'
        )


class AFALicencaMandatoClassistaRestful(AFALicencaRestful):

    full_text_index = () + AFALicencaRestful.full_text_index

    exclude_fields = [] + AFALicencaRestful.exclude_fields

    force_persist_boolean_fields = [] + AFALicencaRestful.force_persist_boolean_fields

    _model = LicencaMandatoClassista

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.licencamandatoclassista.Manage")'
        )


class AFAAwardLicense(AFALicencaRestful):

    full_text_index = () + AFALicencaRestful.full_text_index

    exclude_fields = [] + AFALicencaRestful.exclude_fields

    force_persist_boolean_fields = [] + AFALicencaRestful.force_persist_boolean_fields

    _model = AwardLicense

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.awardlicense.Manage")')


class AFALicencaServicoMilitarRestful(AFALicencaRestful):

    full_text_index = () + AFALicencaRestful.full_text_index

    exclude_fields = [] + AFALicencaRestful.exclude_fields

    force_persist_boolean_fields = [] + AFALicencaRestful.force_persist_boolean_fields

    _model = LicencaServicoMilitar

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.licencaservicomilitar.Manage")'
        )
