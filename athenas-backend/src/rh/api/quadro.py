# -*- coding: utf-8 -*-

from contrib.controller import DefaultController
from contrib.newrest import RestfulDRY
from rh.models import Quadro


class RHQuadroRestful(RestfulDRY):

    _model = Quadro

    full_text_index = ("cargo__nome__icontains", "especialidade__nome__icontains")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.quadro.Manage")')


class RHQuadroProvimentoRestful(DefaultController):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.quadro.QuadroProvimentoManage")')
