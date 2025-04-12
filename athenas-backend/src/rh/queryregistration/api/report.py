from distutils import extension
from contrib.controller import DefaultController
from engine.mq.models import Task
from rh.queryregistration.tasks import report_pdf, report_xls
from contrib.decorator import login_required
from rh.gfp.models import Folha, Evento, FolhaEvento
from contrib.middleware import get_current_user
from contrib.utils import getLogger, get_json_engine
from rh.queryregistration.models import CacheTag, Consultation, TagField
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from rh.queryregistration.const import PORTRAIT, LANDSCAPE
from django.db import connection
from standard.models import Choice
from rh.models import Cargo, Servidor
import ast, re
from functools import partial
import os
from contrib.utils import employee_from_user


log = getLogger(__name__)
json = get_json_engine()


class QueryReport(DefaultController):

    def _extract_params_tag(self, sql):
        """Esse metódo retorna as tags da consulta sql no formato de Dict"""
        reg_str = "\$([^$]+)\$"
        tags_sql = re.findall(reg_str, sql)
        tags = {}
        for tag in tags_sql:
            temp = tag.split(":")
            if len(temp) > 1:
                tags.update({tag: temp[1].lower().replace(" ", "_").replace("?", "")})
            else:
                tags.update({tag: temp[0].lower().replace(" ", "_").replace("?", "")})

        return tags

    def _set_page_orientation(self, orientation):
        html_path = "portrait/querytemplate/template.html"
        if orientation:
            if int(orientation) == LANDSCAPE:
                html_path = "landescape/querytemplate/template.html"

        return html_path

    def _message_success(self, title):
        return f"""<p>{title} - <a href="/athenas/QueryReport/download_file/?uuid=%(uuid)s">Download</a>.</p>"""

    def _create_cache(self, query, params):
        tags = self._extract_params_tag(query.sql)
        for tag in tags:
            try:
                key_tag = tag.split(":")[0].replace("?", "").replace(" ", "_")
                result = TagField.objects.get(key_tag=key_tag)
                key_tag = params.get(tags.get(tag))
                index = list(tags.keys()).index(tag)
                obj, created = CacheTag.objects.update_or_create(
                    field_name=list(tags.keys())[index],
                    report=query,
                    employee=employee_from_user(get_current_user()),
                    tag=result,
                    defaults={
                        "field_name": list(tags.keys())[index],
                        "report": query,
                        "tag": result,
                        "employee": employee_from_user(get_current_user()),
                        "value": key_tag,
                    },
                )
            except Exception as e:
                log.error(e)

    @login_required("JSON")
    def create_pdf(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            pk = self.request.POST.get("pk")
            name_observer = self.request.POST.get("name_observer")
            query = Consultation.objects.get(pk=pk)
            params = ast.literal_eval(self.request.POST.get("tags"))
            self._create_cache(
                query=query, params=ast.literal_eval(self.request.POST.get("tags"))
            )

            path = self._set_page_orientation(params.get("orientation", None))
            Task.start(
                report_pdf,
                f"Gerando Relatório",
                success=self._message_success(query.title.title()),
                user=get_current_user().pk,
                title=query.title,
                params=params,
                tags=self._extract_params_tag(query.sql),
                instance="Consultation",
                pk=pk,
                html_path=path,
                download=query.download,
                filename=f"query-{query.title.lower()}-{get_current_user().pk}.pdf",
                mimetype="application/pdf",
                extension="pdf",
                identifier="queryregistration",
                name_observer=name_observer,
            )
            obj.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                download=query.download,
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
            query = Consultation.objects.get(pk=pk)
            params = ast.literal_eval(self.request.POST.get("tags"))

            Task.start(
                report_xls,
                f"Gerando Relatório",
                success=self._message_success(query.title.title()),
                user=get_current_user().pk,
                title=query.title,
                params=params,
                tags=self._extract_params_tag(query.sql),
                instance="Consultation",
                pk=pk,
                download=query.download,
                filename=f"query-{query.title.lower()}-{get_current_user().pk}.xls",
                mimetype="application/vnd.ms-excel",
                extension="xls",
                identifier="queryregistration",
            )
            obj.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                download=query.download,
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
