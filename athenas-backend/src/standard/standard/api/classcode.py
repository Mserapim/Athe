# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from standard.models import ClassCode

# from contrib.utils import DateUtils


class STDClassCodeRestful(RestfulDRY):

    _model = ClassCode
    force_upper = False

    full_text_index = (
        "title__icontains",
        "path__icontains",
    )

    force_persist_field_boolean = True

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("standard.classcode.Manage")')
