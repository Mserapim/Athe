# -*- coding: utf-8 -*-
from contrib.controller import DefaultController


class SACIReport(DefaultController):

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("common.saci.ReportManage")')
