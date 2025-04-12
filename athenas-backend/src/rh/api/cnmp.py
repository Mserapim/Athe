# -*- coding: utf-8 -*-
from functools import partial
import json

from django.http import HttpResponseBadRequest, HttpResponseNotFound

from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.decorator import login_required
from contrib.controller import DefaultController
from engine.mq.models import Task
from rh.generators.cnmp_report import CNMPReport
from rh.models import (
    CourseAreaCNMP,
    GraduationCNMP,
    ImprovementAndGraduateCNMP,
    PublishedWorksCNMP,
    Servidor,
)
from rh.task.cnmp_report import cnmp_report_maker

log = getLogger(__name__)


class RHFormationCNMP(RestfulDRY):

    _model = Servidor

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.cnmp.FormationManage")')


class RHCourseAreaCNMP(RestfulDRY):

    _model = CourseAreaCNMP

    force_upper = False


class RHGraduationCNMP(RestfulDRY):

    _model = GraduationCNMP

    force_upper = False


class RHImprovementAndGraduateCNMP(RestfulDRY):

    _model = ImprovementAndGraduateCNMP

    force_upper = False


class RHPublishedWorksCNMP(RestfulDRY):

    _model = PublishedWorksCNMP

    force_upper = False


class RHCNMPReport(DefaultController):
    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write("new toolkit.rh.cnmp.DiversityCNMPReport()")

    def renderer(self, data):
        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(data))

    @login_required(type="JSON")
    def start(self, args=[]):
        response_msg = {"success": False, "message": "Nada feito ainda!"}
        try:
            Task.start(
                cnmp_report_maker,
                user=get_current_user().pk,
                success="""<p><span style="font-weight:bold">Relatório de diversidade CNMP</span> foi gerado com sucesso.
                    Para fazer o download clique no <a href="/athenas/RHCNMPReport/file/?uuid=%(uuid)s">link</a>.
                    </p>
                    <p>Este arquivo está disponível para download até dia <span style="font-weight:bold">%(deadline)s</span></p>""",
            )
        except Exception as e:
            response_msg.update(message=str(e))
        else:
            response_msg.update(
                success=True,
                message="Relatório de diversidade CNMP requisitado com sucesso, você será avisado quando o mesmo for concluído.",
            )
        self.renderer(response_msg)

    def file(self, args=[]):
        try:
            task = Task.objects.get(
                uuid=self.request.GET.get("uuid"), owner=self.request.user
            )

            if task.state == "ready":
                data = json.loads(task.data)
                filename = data.get("filename")
                file_path = data.get("file_path")

                self.response["Content-Type"] = "application/xlsx"
                self.response["Content-Disposition"] = (
                    'attachment; filename="%s"' % filename
                )
                with open(file_path, "rb") as fd:
                    for data in iter(partial(fd.read, 8192), b""):
                        self.response.write(data)

                task.save()
            else:
                self.response = HttpResponseNotFound(
                    "<h1>Arquivo do SICAP AP não está pronto ou não foi solicitado.</h1>"
                )
        except Exception as e:
            self.log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Não existe este pedido de arquivo do SICAP AP para o usuário logado.</h1>"
            )
