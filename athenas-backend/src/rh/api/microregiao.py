# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import MicroRegiao


class RHMicroRegiaoRestful(RestfulDRY):

    _model = MicroRegiao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.microregiao.MicroRegiaoManage")')
