# -*- coding: utf-8 -*-

from django import forms
from django.db.models import Q

from contrib import extjs
from contrib.utils import get_json_engine
from rh.const import ESTADO_BASE_LICENCA_AFASTAMENTO, INDICATIVO
from rh.models import Lotacao, Servidor
from rh.reports import get_choice_models
from rh.views import RHServidor
from standard.views import AutoCompleteField

json = get_json_engine()


class AFAPrintProtocoloLicencaSaude(extjs.ExtReportBuild):

    report_src = "/to/mpe/rh/protocolo_licenca/main"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/protocolo_licenca/",
        }
    ]

    titles = {
        "TITLE": "Protocolo Licença Saúde",
        "SUB_TITLE": "Geração de protocolo para licença saúde",
    }

    def get_generated_filename(self):
        return "afastamentoslicenca.pdf"

    class Form(forms.Form):
        servidor = AutoCompleteField(
            model=Servidor,
            label="Servidor",
            controller=RHServidor,
            required=False,
            display_field="description",
            value_field="id",
        )

    def autocomplete(self, args=[]):
        obj = {"result": []}
        if len(args) > 0 and args[0] in ("Servidor"):
            if args[0] == "Servidor":
                for row in Servidor.objects.filter(
                    Q(pessoa_fisica__nome__icontains=self.request.POST["query"])
                    | Q(matricula__icontains=self.request.POST["query"])
                ):
                    obj["result"].append({"id": row.pk, "description": row})
            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))
        else:
            super(AFAPrintProtocoloLicencaSaude, self).autocomplete(args)


class AFAPrintDepartures(extjs.ExtReportBuild):

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/servidor/afastamento_departamento/",
        }
    ]

    report_src = "/to/mpe/rh/servidor/afastamento_departamento/main"
    filename = "afastamentos.pdf"

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Afastamentos"}

    class Form(forms.Form):
        lotacao = forms.ChoiceField(
            label="Lotação/Designação",
            choices=get_choice_models(Lotacao.objects.all().order_by("nome")),
            required=False,
        )
        situacao = forms.ChoiceField(
            label="Situação",
            choices=list(ESTADO_BASE_LICENCA_AFASTAMENTO.items()),
            required=False,
        )
        servidor_tipo = forms.ChoiceField(
            label="Tipo do Servidor", choices=INDICATIVO, required=False
        )
        data_inicial = forms.DateField(label="Data Início", required=True)
        data_final = forms.DateField(label="Data Fim", required=True)
