# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import Cargo, ConfigJobPosition


class RHJobPositionRestful(RestfulDRY):

    full_text_index = (
        "configs__cbo__descricao__icontains",
        "carreira__nome__icontains",
        "nome__icontains",
        "codigo__icontains",
        "lotacao_responsavel__nome__icontains",
    )

    _model = Cargo

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.jobposition.Manage")')


class RHConfigJobPosition(RestfulDRY):

    full_text_index = (
        "cbo__descricao__icontains",
        "name__icontains",
        "code__icontains",
    )

    _model = ConfigJobPosition

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.jobposition.config.Manage")')
