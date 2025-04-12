# -*- coding: utf-8 -*-

from contrib.controller import DefaultController
from contrib.middleware import get_current_user
from contrib.utils import getLogger
from contrib.utils import get_json_engine
from contrib.decorator import login_required
from datetime import datetime
from engine.mq.models import Task
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from rh.gfp.signals.remuneration_base import Period
from rh.gfp.tasks import commitment_report
from rh.gfp.models import Folha
from django.template import loader
import ast
from functools import partial


log = getLogger(__name__)
json = get_json_engine()


class GFPFinancialStatementReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.reports.FinancialStatementManage")')

    def year(self, args=[]):
        obj = {}
        result = []

        for ano in range((datetime.now().year), 1997, -1):
            result.append({"year": ano})

        obj.update(result=result)
        self.response.write(json.encode(obj))


class GFPProofOfIncomeReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.reports.ProofOfIncome")')


class GFPEmployeeByEventType(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.reports.EmployeeByEventType")')


class GFPBillet(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.reports.Billet")')


class GFPCommitmentReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.reports.CommitmentReportManage")')

    @login_required("JSON")
    def create_pdf(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        sheet = self.request.POST.get("sheet")
        period = str(Folha.objects.get(pk=sheet).periodo)
        type = self.request.POST.get("type")
        report = self.request.POST.get("report")
        option = self.request.POST.get("option")
        subtitle = self.request.POST.get("subtitle")

        try:
            Task.start(
                commitment_report,
                f"Gerando Relatório de Empenhos",
                success=f"""<p>Relatório de {report} gerado com sucessso.
                <a href="/athenas/GFPCommitmentReport/viewer/?uuid=%(uuid)s" target="_blank">Visualizar Relatório</a>.
                </p>""",
                user=get_current_user().pk,
                period=period,
                sheet=sheet,
                option=option,
                subtitle=subtitle,
                filename=f"report-{type}-{get_current_user().pk}.pdf",
                type=type,
                mimetype="application/pdf",
                identifier="empenhoslrf",
            )
            obj.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            )
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def viewer(self, *args):
        try:
            task = Task.objects.get(
                uuid=self.request.GET.get("uuid"), owner=get_current_user()
            )
            # if task.state == 'ready':
            data = ast.literal_eval(task.data)
            file = data.get("file")
            self.response["Content-Type"] = "application/pdf"
            with open(file, "rb") as fd:
                for data in iter(partial(fd.read, 8192), b""):
                    self.response.write(data)
            if task.state != "mf-ready":
                task.mark_finished()
            task.save()
            # else:
            #     self.response = HttpResponseNotFound(
            #         '<h1>Erro ao Carregar o Relatório.</h1>')
        except Exception as e:
            log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Erro ao Carregar o Relatório.</h1>"
            )

    def viewer_header(self, *args):
        tpl = loader.get_template("header_report.html")
        self.response.write(tpl.render({}))
