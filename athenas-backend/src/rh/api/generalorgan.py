# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import OrgaoGeral


class RHGeneralOrganRestful(RestfulDRY):

    _model = OrgaoGeral

    full_text_index = (
        "nome__icontains",
        "sigla__icontains",
        "abreviacao__icontains",
        "cache_identifier__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.generalorgan.Manage")')
