# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import DeficiencyInformation


class RHDeficiencyInformation(RestfulDRY):

    _model = DeficiencyInformation

    exclude_fields = []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.deficiencyinformation.Manage")')
