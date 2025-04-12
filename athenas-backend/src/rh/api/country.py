# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import Pais


class RHCountry(RestfulDRY):

    full_text_index = ("nome__icontains",)

    _model = Pais

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.country.Manage")')
