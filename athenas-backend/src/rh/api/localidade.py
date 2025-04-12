# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import Localidade


class RHLocalidadeRestful(RestfulDRY):

    full_text_index = (
        "nome__icontains",
        "cep__icontains",
        "sigla__icontains",
        "ibge__icontains",
    )

    _model = Localidade

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.localidade.Manage")')
