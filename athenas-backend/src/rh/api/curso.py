# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import Curso


class RHCursoRestful(RestfulDRY):

    full_text_index = (
        "nome__icontains",
        "descricao__icontains",
        "area_conhecimento__titulo__icontains",
        "area_conhecimento__codigo_cnpq__icontains",
        "area_conhecimento__cache_codigo_cnpq__icontains",
        "grau_instrucao__icontains",
    )

    _model = Curso

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.curso.Manage")')
