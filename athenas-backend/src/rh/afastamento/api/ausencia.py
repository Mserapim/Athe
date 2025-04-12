# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from rh.afastamento.api.baselicencaafastamento import AFABaseLicencaAfastamentoRestful
from rh.afastamento.models import (
    AusenciaCasamento,
    AusenciaConclusao,
    AusenciaDoacaoSangue,
    AusenciaEleitor,
)
from rh.afastamento.models import AusenciaFalecimento, AusenciaNascimento, Ausencia

log = getLogger(__name__)


class AFAAusenciaRestful(AFABaseLicencaAfastamentoRestful):

    full_text_index = () + AFABaseLicencaAfastamentoRestful.full_text_index

    exclude_fields = [] + AFABaseLicencaAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFABaseLicencaAfastamentoRestful.force_persist_boolean_fields
    )

    _model = Ausencia

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.ausencia.Manage")')


class AFAAusenciaCasamentoRestful(AFAAusenciaRestful):

    full_text_index = () + AFAAusenciaRestful.full_text_index

    exclude_fields = [] + AFAAusenciaRestful.exclude_fields

    force_persist_boolean_fields = [] + AFAAusenciaRestful.force_persist_boolean_fields

    _model = AusenciaCasamento

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.ausenciacasamento.Manage")')


class AFAAusenciaConclusaoRestful(AFAAusenciaRestful):

    full_text_index = () + AFAAusenciaRestful.full_text_index

    exclude_fields = [] + AFAAusenciaRestful.exclude_fields

    force_persist_boolean_fields = [] + AFAAusenciaRestful.force_persist_boolean_fields

    _model = AusenciaConclusao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.ausenciaconclusao.Manage")')


class AFAAusenciaDoacaoSangueRestful(AFAAusenciaRestful):

    full_text_index = () + AFAAusenciaRestful.full_text_index

    exclude_fields = [] + AFAAusenciaRestful.exclude_fields

    force_persist_boolean_fields = [] + AFAAusenciaRestful.force_persist_boolean_fields

    _model = AusenciaDoacaoSangue

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.ausenciadoacaosangue.Manage")')


class AFAAusenciaEleitorRestful(AFAAusenciaRestful):

    full_text_index = () + AFAAusenciaRestful.full_text_index

    exclude_fields = [] + AFAAusenciaRestful.exclude_fields

    force_persist_boolean_fields = [] + AFAAusenciaRestful.force_persist_boolean_fields

    _model = AusenciaEleitor

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.ausenciaeleitor.Manage")')


class AFAAusenciaFalecimentoRestful(AFAAusenciaRestful):

    full_text_index = () + AFAAusenciaRestful.full_text_index

    exclude_fields = [] + AFAAusenciaRestful.exclude_fields

    force_persist_boolean_fields = [] + AFAAusenciaRestful.force_persist_boolean_fields

    _model = AusenciaFalecimento

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.ausenciafalecimento.Manage")')


class AFAAusenciaNascimentoRestful(AFAAusenciaRestful):

    full_text_index = () + AFAAusenciaRestful.full_text_index

    exclude_fields = [] + AFAAusenciaRestful.exclude_fields

    force_persist_boolean_fields = [] + AFAAusenciaRestful.force_persist_boolean_fields

    _model = AusenciaNascimento

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.afastamento.ausencianascimento.Manage")')
