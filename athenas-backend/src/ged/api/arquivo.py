# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from ged.models import Arquivo


class GEDArquivoRestful(RestfulDRY):

    _model = Arquivo

    full_text_index = (
        "filename__icontains",
        "user__username__icontains",
        "group__nome__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("ged.arquivo.ArquivoManage")')
