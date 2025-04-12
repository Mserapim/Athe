# -*- coding: utf-8 -*-

from django import forms

from contrib import extjs
from contrib.newrest import Restful
from contrib.utils import DateUtils, employee_from_user, get_json_engine, getLogger
from rh.models import CensoPrevidenciario, MovimentacaoPosse

# from datetime import *
json = get_json_engine()
log = getLogger(__name__)


PREVIDENCIARIO_CHOICES = (
    (1, "REGIME GERAL DE PREVIDÊNCIA"),
    (2, "REGIME PRÓPRIO DE PREVIDÊNCIA"),
)


class RHCensoPrevidenciario(Restful):

    _model = CensoPrevidenciario

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__iexact",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('rh.pesquisa.PrevidenciarioTabPanel')")

    def model_to_dict(self, instance):
        params = Restful.model_to_dict(self, instance)

        params.update(
            {
                "servidor_unicode": "%s" % instance.servidor,
                "servidor": instance.servidor_id,
                "tipo_regime_display": instance.get_tipo_regime_display(),
                "tipo_regime": instance.tipo_regime,
                "empresa_orgao": instance.empresa_orgao,
                "data_inicio": (
                    DateUtils.date_to_str(instance.data_inicio)
                    if instance.data_inicio
                    else None
                ),
                "data_fim": (
                    DateUtils.date_to_str(instance.data_fim)
                    if instance.data_fim
                    else None
                ),
                "data_nascimento": (
                    DateUtils.date_to_str(
                        instance.servidor.pessoa_fisica.data_nascimento
                    )
                    if instance.servidor.pessoa_fisica.data_nascimento
                    else None
                ),
                "idade": instance.servidor.pessoa_fisica.idade,
                "dias": instance.dias,
            }
        )
        return params

    def get_params(self, querydict=None, **kargs):
        params = super(RHCensoPrevidenciario, self).get_params(querydict, **kargs)
        dias = 0

        if "data_inicio" in params and "data_fim" in params:
            if params.get("data_inicio", "") == "" or params.get("data_fim", "") == "":
                raise Exception("Data Início e Data Fim Obrigatórios")

            params.update(data_inicio=DateUtils.str_to_date(params.get("data_inicio")))
            params.update(data_fim=DateUtils.str_to_date(params.get("data_fim")))

            data_inicio = params.get("data_inicio")
            data_fim = params.get("data_fim")
            dif_date = data_fim - data_inicio
            dias = dif_date.days if dif_date.days > 0 else 0
            dias = dias + 1

        params.update(dias=dias)
        params.update(servidor=employee_from_user(self.request.user))

        return params

    def get_query(self):
        query = super(RHCensoPrevidenciario, self).get_query()

        if self.request.user.has_perm("censo_prev_admin") is False:
            query = query.filter(servidor=employee_from_user(self.request.user))

        return query

    def has_permission(self, args=[]):
        obj = {
            "result": (
                False
                if MovimentacaoPosse.objects.filter(
                    servidor__matricula=self.request.user.servidor.matricula,
                    quadro__cargo__tipo_lei_cargo="EF",
                    ativo=True,
                    servidor__tipo__in=["S", "M"],
                ).count()
                else True
            )
        }

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class RHRelatorioCensoPrevidenciario(extjs.ExtReportBuild):
    report_src = "/to/mpe/rh/censo_previdenciario/main"
    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/censo_previdenciario/",
        }
    ]

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Relatório Censo Previdenciário"}

    class Form(forms.Form):
        regime = forms.ChoiceField(
            label="Tipo de Regime", choices=PREVIDENCIARIO_CHOICES, required=False
        )

    def get_generated_filename(self):
        dic = dict(PREVIDENCIARIO_CHOICES)
        report = (
            "relatorio-censo-previdenciario-%s.pdf"
            % dic.get(int(self.request.GET["regime"]))
            if self.request.GET["regime"]
            else "relatorio-censo-previdenciario-geral.pdf"
        )
        report = report.encode("utf-8")
        return report
