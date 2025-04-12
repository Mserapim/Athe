# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import Documento


class RHDocumentoRestful(RestfulDRY):

    _model = Documento

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.documento.DocumentoManage")')
