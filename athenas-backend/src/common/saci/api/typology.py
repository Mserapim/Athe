# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from common.saci.models import Typology


class SACITypology(RestfulDRY):
    _model = Typology

    full_text_index = ("name__icontains",)
    force_upper = True
    force_orm_single = True

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.saci.typology.Manage")')
