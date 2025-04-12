# -*- coding: utf-8 -*-
from contrib import extjs
from django import forms
from cesaf.concurso.models import Concurso
from django.template.defaultfilters import slugify


class CONCURSOReport(extjs.ExtReportBuild):

    titles = {"TITLE": "Relatório", "SUB_TITLE": "Concurso detalhado"}

    params = [
        {"nome": "SUBREPORT_DIR", "valor": "to/mpe/cesaf/gecap/", "tipo": "string"}
    ]

    report_src = "/to/mpe/cesaf/gecap/concurso_detalhado"

    class Form(forms.Form):
        concurso = forms.ModelMultipleChoiceField(
            queryset=Concurso.objects.all(), label="Concurso"
        )

    def get_generated_filename(self):
        title = "undefined"

        try:
            c = Concurso.objects.get(pk=int(self.request.GET["concurso"]))
            title = c.nome
        except Exception as e:
            self.log.exception(e)

        return slugify("resumo %s" % title) + ".pdf"
