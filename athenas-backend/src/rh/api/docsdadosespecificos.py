# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import DocsDadosEspecificos


class RHDocsDadosEspecificosRestful(RestfulDRY):

    _model = DocsDadosEspecificos

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.documento.specificdata.Manage")')
