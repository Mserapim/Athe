# -*- coding: utf-8 -*-
# from django import forms
# from django.template.defaultfilters import slugify
# from rh.gfp import models
# from rh.gfp.views import CustomAutocomplete
# from rh.gfp.dirf.models import Demonstrativo
# from rh.models import Servidor, Cargo
# from standard.views import AutoCompleteField
# from datetime import datetime
# from unicodedata import normalize

from contrib.extjs import ExtReportBuild


class PTReports(ExtReportBuild):

    report_src = "/to/mpe/portaltransparencia/rh/afastados"
    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "/to/mpe/portaltransparencia/rh/",
        }
    ]

    def run_report(self, args=[]):
        try:
            if "report" in self.request.POST:
                self.report_src = "%s%s" % (
                    "/to/mpe/portaltransparencia/rh/",
                    self.request.POST.get("report"),
                )
        except Exception:
            pass
        return super(PTReports, self).run_report(args)
