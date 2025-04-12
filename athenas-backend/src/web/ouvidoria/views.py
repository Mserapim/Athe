# -*- coding: utf-8 -*-
import datetime

from django.db.models import Count
from django import forms as django_forms

from contrib.extjs import ExtReportBuild
from contrib.helpers import PublicReportWrapperFacotry

from contrib.controller import ContentType, JsonResponseController
from contrib.decorator import is_public

from edocs.protocolo.models import Protocolo
from web.ouvidoria.choices import ASSUNTO

BASE_TEMPLATE = "ouvidoria/templates/template.html"


def redirect(env, url):
    redirect = (
        """
        <html>
            <head>
                <meta http-equiv="refresh" content="0;URL=%s">
            </head>
        </html>
    """
        % url
    )
    env.response.write(redirect)


class ReportBuilder(ExtReportBuild):

    class Form(django_forms.Form):
        data_inicio = django_forms.CharField()
        data_fim = django_forms.CharField()

    report_src = "/to/mpe/ouvidoria/sintetico/main"
    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/ouvidoria/sintetico/",
        }
    ]

    def get_generated_filename(self):
        start = self.PARAMS["data_inicio"]
        end = self.PARAMS["data_fim"]
        return "relatorio-de-ouvidoria-periodo-%s-a-%s.pdf" % (start, end)


PublicReportWrapper = PublicReportWrapperFacotry(ReportBuilder)


class OuvidoriaReport(PublicReportWrapper):
    pass


class Ouvidoria(JsonResponseController):

    @is_public()
    def index(self, args=[]):
        # descomentar a linha abaixo quando entrar em recesso
        return redirect(self, "http://mpto.mp.br/web/ouvidoria")
        # return self.render_template(BASE_TEMPLATE)

    @is_public()
    @ContentType("text/javascript")
    def count_report(self, args=[]):
        start_date = self.request.REQUEST.get("start-date")
        end_date = self.request.REQUEST.get("end-date")

        end_date = (
            datetime.datetime.strptime(end_date, "%Y-%m-%d")
            if end_date
            else datetime.date.today()
        )
        start_date = (
            datetime.datetime.strptime(start_date, "%Y-%m-%d")
            if start_date
            else end_date - datetime.timedelta(days=30)
        )
        subjects = dict(ASSUNTO[1:])
        params = {
            "tipo_documento__nome": "OUVIDORIA",
            "assunto__in": list(subjects.keys()),
            "data_criacao__range": (start_date, end_date),
        }

        qs = Protocolo.objects.filter(**params)

        received = (
            qs.values("assunto").annotate(total=Count("assunto")).order_by("assunto")
        )
        forward = received.filter(movimentacoes__passo=1).order_by("assunto")
        finished = forward.filter(data_finalizado__isnull=False).order_by("assunto")
        statuses = {
            "received": list(received),
            "forward": list(forward),
            "finished": list(finished),
        }

        report = {"received": 0, "forward": 0, "finished": 0}
        touches = {}
        for status, items in list(statuses.items()):
            for item in items:
                touch = touches.get(
                    item["assunto"], {"received": 0, "forward": 0, "finished": 0}
                )
                touch["assunto"] = item["assunto"]
                touch[status] = item["total"]
                report[status] += item["total"]
                touches[item["assunto"]] = touch

        report.update(
            {
                "list": sorted(
                    list(touches.values()), key=lambda touch: touch["assunto"]
                ),
                "total": len(touches),
            }
        )

        self.render(report)
