# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import Comarca


class RHComarcaRestful(RestfulDRY):

    full_text_index = (
        "nome__icontains",
        "descricao__icontains",
        "circunscricao__nome__icontains",
        "circunscricao__descricao__icontains",
        "grupo_comarca__nome__icontains",
        "grupo_comarca__descricao__icontains",
    )

    _model = Comarca

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.comarca.ComarcaManage")')
