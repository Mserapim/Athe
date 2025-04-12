# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import NecessidadeEspecial


class RHNecessidadeEspecialRestful(RestfulDRY):

    _model = NecessidadeEspecial

    full_text_index = ("nome__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.necessidadeespecial.Manage")')
