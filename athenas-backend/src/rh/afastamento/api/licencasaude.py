# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from rh.afastamento.api.licenca import AFALicencaRestful
from rh.afastamento.models import (
    LicencaAdocao,
    LicencaDoencaPessoaFamilia,
    LicencaMaternidade,
    LicencaSaude,
    LicencaSaude3Dias,
    LicencaSaude30Dias,
    LicencaSaudeHoras,
    LicencaSaudeJuntaMedica,
)

log = getLogger(__name__)


class AFALicencaSaudeRestful(AFALicencaRestful):

    full_text_index = () + AFALicencaRestful.full_text_index

    exclude_fields = [] + AFALicencaRestful.exclude_fields

    force_persist_boolean_fields = [] + AFALicencaRestful.force_persist_boolean_fields

    _model = LicencaSaude

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.licencasaude.Manage")')


class AFALicencaSaude3DiasRestful(AFALicencaSaudeRestful):

    full_text_index = () + AFALicencaSaudeRestful.full_text_index

    exclude_fields = [] + AFALicencaSaudeRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFALicencaSaudeRestful.force_persist_boolean_fields
    )

    _model = LicencaSaude3Dias

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.licencasaude3dias.Manage")')


class AFALicencaSaudeHorasRestful(AFALicencaSaudeRestful):

    full_text_index = () + AFALicencaSaudeRestful.full_text_index

    exclude_fields = [] + AFALicencaSaudeRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFALicencaSaudeRestful.force_persist_boolean_fields
    )

    _model = LicencaSaudeHoras

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.licencasaudehoras.Manage")')


class AFALicencaSaude30DiasRestful(AFALicencaSaudeRestful):

    full_text_index = () + AFALicencaSaudeRestful.full_text_index

    exclude_fields = [] + AFALicencaSaudeRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFALicencaSaudeRestful.force_persist_boolean_fields
    )

    _model = LicencaSaude30Dias

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.licencasaude30dias.Manage")')


class AFALicencaSaudeJuntaMedicaRestful(AFALicencaSaudeRestful):

    full_text_index = () + AFALicencaSaudeRestful.full_text_index

    exclude_fields = [] + AFALicencaSaudeRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFALicencaSaudeRestful.force_persist_boolean_fields
    )

    _model = LicencaSaudeJuntaMedica

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.licencasaudejuntamedica.Manage")'
        )


class AFALicencaDoencaPessoaFamiliaRestful(AFALicencaSaudeJuntaMedicaRestful):

    full_text_index = () + AFALicencaSaudeJuntaMedicaRestful.full_text_index

    exclude_fields = [] + AFALicencaSaudeJuntaMedicaRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFALicencaSaudeJuntaMedicaRestful.force_persist_boolean_fields
    )

    _model = LicencaDoencaPessoaFamilia

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.afastamento.licencadoencapessoafamilia.Manage")'
        )


class AFALicencaMaternidadeRestful(AFALicencaSaudeJuntaMedicaRestful):

    full_text_index = () + AFALicencaSaudeJuntaMedicaRestful.full_text_index

    exclude_fields = [] + AFALicencaSaudeJuntaMedicaRestful.exclude_fields

    force_persist_boolean_fields = [
        "natimorto"
    ] + AFALicencaSaudeJuntaMedicaRestful.force_persist_boolean_fields

    _model = LicencaMaternidade

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.licencamaternidade.Manage")')


class AFALicencaAdocaoRestful(AFALicencaSaudeJuntaMedicaRestful):

    full_text_index = () + AFALicencaSaudeJuntaMedicaRestful.full_text_index

    exclude_fields = [] + AFALicencaSaudeJuntaMedicaRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFALicencaSaudeJuntaMedicaRestful.force_persist_boolean_fields
    )

    _model = LicencaAdocao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.licencaadocao.Manage")')
