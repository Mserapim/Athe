# -*- coding: utf-8 -*-
import os
import json

from django.http import HttpResponseBadRequest, HttpResponseNotFound
from contrib.controller import DefaultController
from engine.mq.models import Task
from contrib.reports import start_report
from contrib.jasper import Client
from django.conf import settings
from contrib.utils import getLogger
from functools import partial

log = getLogger(__name__)


class MQReportBuilder(DefaultController):

    _default_filename = "not-implemented"

    _default_report_name = "REPORT_NAME"

    def _report_name(self, report_name=None, **kwargs):
        return report_name if report_name else self._default_report_name

    def _filename(self, outfile=None, **kwargs):
        return outfile if outfile else self._default_filename

    def renderer(self, data):
        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(data))

    def file(self, args=[]):
        cache_path = getattr(settings, "CACHE", {}).get("jreport", None)

        try:
            task = Task.objects.get(
                uuid=self.request.GET.get("uuid"), owner=self.request.user
            )

            formats = {
                "PDF": ["application/pdf", "pdf"],
                "CSV": ["text/csv", "csv"],
                "XLS": ["application/vnd.ms-excel", "xls"],
                "ODT": ["application/vnd.oasis.opendocument.text", "odt"],
                "ODS": ["application/vnd.oasis.opendocument.spreadsheet", "ods"],
            }

            mimetype, ext = formats.get(
                self.request.GET.get("output_format", "PDF"),
                [
                    self.request.GET.get("output_mimetype", "application/octstream"),
                    self.request.GET.get("output_extension", "bin"),
                ],
            )

            if task.state == "ready":
                data = json.loads(task.data)
                filename = os.path.join(
                    cache_path, "-".join([data.get("queue"), data.get("outid")])
                )
                params = json.loads(task.params)

                self.response["Content-Type"] = mimetype
                self.response["Content-Disposition"] = (
                    'attachment; filename="%(filename)s.%(extension)s"'
                    % {
                        "filename": self._filename(**params.get("params", {})),
                        "extension": ext,
                    }
                )
                with open(filename, "rb") as fd:
                    for data in iter(partial(fd.read, 8192), b""):
                        self.response.write(data)

                task.state = "downloaded"
                task.save()
            else:
                self.response = HttpResponseNotFound(
                    "<h1>Relatório não esta pronto ou não foi solicitado.</h1>"
                )
        except Exception as e:
            self.log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Não existe este pedido de relatório para o usuário logado.</h1>"
            )

    def start(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            params = json.loads(self.request.POST.get("params"))
            if not "organ_identifier" in params:
                params["organ_identifier"] = settings.ORGAN_IDENTIFIER
            report = self.request.POST.get("report")

            if getattr(settings, "REPORT_DEFAULT_PATH", None):
                report = "".join(["/", settings.REPORT_DEFAULT_PATH, report])

            t = Task.start(
                start_report,
                report=report,
                report_name=self._report_name(**params),
                params=params,
                output_format=self.request.POST.get("output_format", "PDF"),
                success="""<p>O Relatorio <span style="font-weight:bold">%(report_name)s</span> foi gerado com sucesso. Para fazer o download clique no
        <a href="/athenas/MQReportBuilder/file/?uuid=%(task)s&output_format=%(output_format)s">link</a>.
    </p>
    <p>Esta relatório estara disponivel para download até dia <span style="font-weight:bold">%(deadline)s</span></p>""",
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            )

        self.renderer(rst)
