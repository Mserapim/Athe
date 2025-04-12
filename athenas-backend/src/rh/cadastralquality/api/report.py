from contrib.controller import DefaultController
from engine.mq.models import Task
from rh.queryregistration.tasks import report_pdf, report_xls
from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.utils import getLogger, get_json_engine
from rh.cadastralquality.models import RegistrationQuery
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from rh.queryregistration.api.report import QueryReport
import ast
from functools import partial
import os


log = getLogger(__name__)
json = get_json_engine()


class CQualityReport(QueryReport):

    def _message_success(self, title):
        return f"""<p>{title} - <a href="/athenas/CQualityReport/download_file/?uuid=%(uuid)s">Download</a>.</p>"""

    @login_required("JSON")
    def create_pdf(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            pk = self.request.POST.get("pk")
            query = RegistrationQuery.objects.get(pk=pk)

            Task.start(
                report_pdf,
                f"Gerando Relatório",
                success=self._message_success(query.title.title()),
                user=get_current_user().pk,
                title=query.title,
                params=[],
                tags=self._extract_params_tag(query.sql),
                instance="RegistrationQuery",
                pk=pk,
                html_path="landescape/querytemplate/template.html",
                download=False,
                filename=f"query-{query.title.lower()}-{get_current_user().pk}.pdf",
                mimetype="application/pdf",
                extension="pdf",
                identifier="cadastralquality",
                save_log=False,
            )
            obj.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                download=False,
            )
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def create_xls(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            pk = self.request.POST.get("pk")
            query = RegistrationQuery.objects.get(pk=pk)

            Task.start(
                report_xls,
                f"Gerando Relatório",
                success=self._message_success(query.title.title()),
                user=get_current_user().pk,
                title=query.title,
                params=[],
                tags=self._extract_params_tag(query.sql),
                instance="RegistrationQuery",
                pk=pk,
                download=False,
                filename=f"query-{query.title.lower()}-{get_current_user().pk}.xls",
                mimetype="application/vnd.ms-excel",
                extension="xls",
                identifier="cadastralquality",
                save_log=False,
            )
            obj.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                download=False,
            )
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def download_file(self, *args):
        try:
            task = Task.objects.get(
                uuid=self.request.GET.get("uuid"), owner=get_current_user()
            )
            if task.state == "ready":
                data = ast.literal_eval(task.data)
                file = data.get("file")
                filename = data.get("filename")
                mimetype = data.get("mimetype")
                extension = data.get("extension")
                self.response["Content-Type"] = mimetype
                self.response["Content-Disposition"] = (
                    'attachment; filename="%(filename)s.%(extension)s"'
                    % {"filename": filename, "extension": extension}
                )
                with open(file, "rb") as fd:
                    for data in iter(partial(fd.read, 8192), b""):
                        self.response.write(data)
                task.mark_finished()
                task.save()
                os.unlink(file)
            else:
                self.response = HttpResponseNotFound(
                    "<h1>Erro ao Carregar o Relatório.</h1>"
                )
        except Exception as e:
            log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Erro ao Carregar o Relatório.</h1>"
            )
