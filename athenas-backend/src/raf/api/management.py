# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from raf.models import FunctionalActivityReport


class RAFManagement(RestfulDRY):
    _model = FunctionalActivityReport
    force_upper = False

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("raf.management.Launcher")')
