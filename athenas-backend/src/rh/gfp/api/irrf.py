# -*- coding: utf-8 -*-

import ast
from functools import partial
import os
from celery import Celery
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user, getLogger, get_json_engine
from contrib.decorator import login_required

from django.http import HttpResponseBadRequest, HttpResponseNotFound
from engine.mq.models import Task
from ged.models import Arquivo
from rh.gfp.models import IRRF, IRRFFaixa
from rh.gfp.tasks import get_cedula_c, task_import_cedula_c
from rh.models import Servidor


app = Celery("queryregistration")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
log = getLogger(__name__)


class GFPIRRF(RestfulDRY):

    _model = IRRF

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.irrf.IRRFManage")')


class GFPIRRFFaixa(RestfulDRY):

    _model = IRRFFaixa


class CedulaCIRPF(RestfulDRY):
    """
    Classe de API view para Importar o relatório de cédula C
    """

    _model = IRRF

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.irrf.cedulaC.CedulaCManage")')

    def import_cedula_c(self, *args):
        """
        Função que recebe parâmetros 'file' e 'year' da requisição e promove a divisão do arquivo (file),
        em Cédulas-C divididas por Servidor
        """
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            can = self.check_permission(
                self.request.user,
                "change",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                obj.update(
                    message="Você não tem permissão para importar %s."
                    % self.Model._meta.object_name
                )
            else:
                arquivo = Arquivo.objects.get(
                    pk=int(self.request.POST.get("file", None))
                )
                retification = (
                    "R" if self.request.POST.get("retification", None) else ""
                )
                year = int(self.request.POST.get("year", None))
                type_cedula_c = self.request.POST.get("type", None)
                Task.start(
                    task_import_cedula_c,
                    "Gerando Relatório",
                    success=f"Importação do Informe de Rendimentos {year} concluída com sucesso",
                    user=get_current_user().pk,
                    path=arquivo.absolute_path,
                    reference=f"{retification}{year}-{type_cedula_c}",
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
        self.response.write(get_json_engine().encode(obj))

    def _message_success(self):
        """
        Mensagem de sucesso de criação de relatório
        """
        return """
            <p>Faça o Download do Informe de Rendimentos
            <a href="/athenas/CedulaCIRPF/download_file/?uuid=%(uuid)s">Download</a>.</p>
        """

    @login_required("JSON")
    def create_pdf_cedula_c(self, *args):
        """
        Função que recebe parâmetros 'employee', 'year' e 'type' da requisição e promove e inicia a tarefa de geração
        da Cédula-c do servidor passado como parâmetro.
        Caso seja passada o parâmetro 'download' como verdadeiro, será feito download automático.
        """
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            employee_pk = self.request.POST.get(
                "employee", employee_from_user(get_current_user()).pk
            )
            year = int(self.request.POST.get("year", None))
            type_cedula_c = self.request.POST.get("type", None)
            download = bool(self.request.POST.get("download", False))
            retification = "R"

            document = Arquivo.objects.filter(
                user=Servidor.objects.filter(pk=employee_pk).first().user,
                filename__icontains=f"cedula-c-{retification}{year}-{type_cedula_c}",
            ).last()
            if not document:
                document = Arquivo.objects.filter(
                    user=Servidor.objects.filter(pk=employee_pk).first().user,
                    filename__icontains=f"cedula-c-{year}-{type_cedula_c}",
                ).first()

            if document:
                task = Task.start(
                    get_cedula_c,
                    "cedula-c-report",
                    success=self._message_success(),
                    user=get_current_user().pk,
                    params=[],
                    document_pk=document.pk,
                    extension="pdf",
                    download=download,
                )
                obj.update(
                    success=True,
                    message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                    download=False,
                    uuid=task.uuid,
                )
            else:
                obj.update(
                    success=False,
                    message="O servidor ainda não possui Cédula-C cadastrada para a referência informada.",
                )
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(get_json_engine().encode(obj))

    @login_required("JSON")
    def download_file(self, *args):
        """
        Função que promove o Download do arquivo do Informe de Rendimentos
        """
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
            else:
                self.response = HttpResponseNotFound(
                    "<h1>Erro ao Carregar o Relatório.</h1>"
                )
        except Exception as e:
            log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Erro ao Carregar o Relatório.</h1>"
            )

    @login_required("JSON")
    def marker(self, *args):
        """
        Função que finaliza uma task
        """
        try:
            task = Task.objects.get(
                uuid=self.request.POST.get("uuid"), owner=get_current_user()
            )
            if task.finished is False:
                task.mark_finished()
                task.data = ""
                task.save()
        except Exception as e:
            log.exception(e)


class CedulaCIRPFReport(RestfulDRY):
    """
    Classe de API que retornar a view para impressão de 'Informe de Rendimentos Admin'
    """

    _model = IRRF

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.reports.CedulaCAdminReport")')
