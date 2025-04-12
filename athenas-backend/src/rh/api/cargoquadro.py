# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import CargoQuadro


class RHJoPositionTableRestful(RestfulDRY):

    full_text_index = (
        "especialidade__nome__icontains",
        "especialidade__descricao__icontains",
        "especialidade__sigla__icontains",
        "cargo__nome__icontains",
        "cargo__descricao__icontains",
    )

    _model = CargoQuadro

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.jobpositiontable.Manage")')
