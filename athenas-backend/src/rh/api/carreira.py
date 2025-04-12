# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import Carreira, ConfigCareer, ExperienciaProfissional

from contrib.utils import getLogger

log = getLogger(__name__)


class RHCarreiraRestful(RestfulDRY):

    full_text_index = (
        "codigo__icontains",
        "nome__icontains",
        "descricao__icontains",
    )

    _model = Carreira

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.carreira.Manage")')


class RHConfigCareer(RestfulDRY):

    full_text_index = (
        "name__icontains",
        "code__icontains",
    )

    _model = ConfigCareer

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.jobposition.config.Manage")')


class RHExperienciaProfissionalRestful(RestfulDRY):

    full_text_index = (
        "cargo__icontains",
        "empregador__icontains",
    )

    _model = ExperienciaProfissional

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.carreira.experiencia_profissional.Manage")'
        )
