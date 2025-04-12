# -*- coding: utf-8 -*-
from contrib import extjs
from django import forms
from cesaf.gecap.models import Capacitacao
from django.template.defaultfilters import slugify


class GCAPReportCapacitacao(extjs.ExtReportBuild):

    titles = {
        "TITLE": "Resumo Detalhado",
        "SUB_TITLE": "Resumo Detalhado de Capacitação",
    }

    params = [
        {"nome": "SUBREPORT_DIR", "valor": "to/mpe/cesaf/gecap/", "tipo": "string"}
    ]

    # report_src = '/to/mpe/cesaf/gecap/capacitacao'
    report_src = "/to/mpe/cesaf/gecap/capacitacao_investimento_geral_detalhado"

    class Form(forms.Form):
        capacitacao = forms.ModelChoiceField(
            queryset=Capacitacao.objects.all(), label="Capacitação"
        )

    def get_generated_filename(self):
        title = "undefined"

        try:
            c = Capacitacao.objects.get(pk=int(self.request.GET["capacitacao"]))
            title = c.nome
        except Exception as e:
            self.log.exception(e)

        return slugify("resumo %s" % title) + ".pdf"


class GCAPReportCapacitacaoGeral(extjs.ExtReportBuild):

    titles = {"TITLE": "Resumo Geral", "SUB_TITLE": "Resumo de Capacitação"}

    filename = "capacitações_resumo_geral.pdf"
    params = [
        {"nome": "SUBREPORT_DIR", "valor": "to/mpe/cesaf/gecap/", "tipo": "string"}
    ]

    report_src = "/to/mpe/cesaf/gecap/capacitacao_investimento_geral"

    class Form(forms.Form):
        data_inicial = forms.DateField(label="Data Início", required=True)
        data_final = forms.DateField(label="Data Fim", required=True)
