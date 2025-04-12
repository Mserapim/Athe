# -*- coding: utf-8 -*-
import re
import json

from contrib.decorator import login_required
from contrib.controller import DefaultController


class EJudReportManage(DefaultController):

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("judicial.reports.ReportManage")')


class EJudReportCnmpManage(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("judicial.reports.CnmpReportWindow")')
