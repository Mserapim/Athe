# -*- coding: utf-8 -*-
from django.conf import settings

from contrib.controller import DefaultController
from contrib.decorator import login_required


class PHMFiscalList(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("planning.hiring.minutereport.FiscalReportList")'
        )


class PHMContractAdditivesTerm(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("planning.hiring.minutereport.ContractAdditivesTerm")'
        )
