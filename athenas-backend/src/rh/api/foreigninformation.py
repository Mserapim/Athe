# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import ForeignInformation


class RHForeignInformation(RestfulDRY):

    _model = ForeignInformation

    exclude_fields = []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.foreigninformation.Manage")')
