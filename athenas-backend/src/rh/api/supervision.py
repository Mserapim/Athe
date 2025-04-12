# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import Supervision


class RHSupervision(RestfulDRY):

    _model = Supervision

    full_text_index = ("name__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.supervision.manage")')
