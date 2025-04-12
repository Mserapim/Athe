# -*- coding: utf-8 -*-
from contrib import extjs
from django import forms


class SPCContratoAcompanha(extjs.ExtReportBuild):

    report_src = "/to/mpe/planejamento/contrato/acompanhamento/main"

    titles = {"TITLE": "Contrato", "SUB_TITLE": "Acompanhamento de Contratos"}

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/planejamento/contrato/acompanhamento/",
        },
    ]

    filename = "acompanhamento_contrato.pdf"

    class Form(forms.Form):
        processo = forms.CharField(label="Nº Processo", required=True)
        contrato = forms.CharField(label="Nº Contrato", required=False)
