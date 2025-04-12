# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import Estado


class RHEstadoRestful(RestfulDRY):

    full_text_index = (
        "nome__icontains",
        "descricao__icontains",
        "pais__nome__icontains",
        "pais__descricao__icontains",
        "pais__ddi__icontains",
        "pais__nome_completo__icontains",
        "pais__nacionalidade__icontains",
        "sigla__icontains",
        "siafi__icontains",
        "ibge__icontains",
    )

    _model = Estado

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.estado.Manage")')
