import os
import ast
from contrib.controller import DefaultController
from contrib.middleware import get_current_user
from contrib.utils import getLogger, get_json_engine
from contrib.decorator import login_required
from engine.mq.models import Task
from reports.tasks import (
    create_docx_task,
    pdf_task,
    report_csv,
    report_xls,
)
from functools import partial
from django.http import HttpResponseBadRequest, HttpResponseNotFound


log = getLogger(__name__)
json = get_json_engine()


class MPMTReports(DefaultController):

    @classmethod
    def get_context_data(self, params={}):
        """
        Método que retorna as informações de contexto para criação do relatório
        :params params: (dict) Dicionário de parâmentros para filtros do relatório
        :returns: (dict) Dicionário contendo dados para gerar o relatório
        """
        return params

    def get_module(self):
        """
        Metódo que retorna o nome o path do módulo da classe
        """
        return f"{self.__module__}"

    def class_name(self):
        """
        Metódo que retorna o nome da classe
        """
        return f"{self.__class__.__name__}"

    def generates_xls(self, report, params, keys=None, download=True):
        """
        Função responsável por iniciar a task de construção de relatório em XLS.

        Parâmetros:
            report: Caminho do template do relatório solicitado
                report: '/to/mpe/gfp/employee_by_consignee'

            params: Parâmetros pertinentes ao relatório
                # mandar como **kwargs
                params: {
                    outfile: 'resumo-de-evento-por-consignatario-folha-' + description,
                    report_name: 'Resumo de Evento - por Consignatário',
                    folha: payroll,
                    plano: plan,
                    employee_type: employee_type
                }
            keys: Parâmetros contendo lista de strings, referente aos nomes dos headers(cabeçalhos) da planilha
                list: [
                    'Primeiro Cabeçalho', 'Segundo Cabeçalho'
                ]
        """

        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            task = Task.start(
                report_xls,
                f"Gerando {params['report_name']}",
                success=f"""<p>{params['report_name']} gerado com sucessso.
                <a href="/athenas/MPMTReports/download_file/?uuid=%(uuid)s" target="_blank">Download</a>.
                </p>""",
                user=get_current_user().pk,
                html_path=report,
                download=download,
                filename=f"{params['report_name'].lower()}",
                mimetype="application/vnd.ms-excel",
                extension="xls",
                identifier="queryregistration",
                path=self.get_module(),
                class_name=self.class_name(),
                params=params,
                keys=keys,
            )
            obj.update(
                success=True,
                uuid=task.uuid,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                download=True,
            )
        except Exception as error:
            log.exception(error)
            obj.update(message="{}".format(error))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def generates_pdf(self, report, params, download=True):
        """
        Parâmetros:
            report: Caminho do template do relatório solicitado
                report: '/to/mpe/gfp/employee_by_consignee'

            params: Parâmetros pertinentes ao relatório
                # mandar como **kwargs
                params: {
                    outfile: 'resumo-de-evento-por-consignatario-folha-' + description,
                    report_name: 'Resumo de Evento - por Consignatário',
                    folha: payroll,
                    plano: plan,
                    employee_type: employee_type
                }
        """

        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            task = Task.start(
                pdf_task,
                f"Gerando {params['report_name']}",
                success=f"""<p>{params['report_name']} gerado com sucessso.
                <a href="/athenas/MPMTReports/download_file/?uuid=%(uuid)s" target="_blank">Download</a>.
                </p>""",
                user=get_current_user().pk,
                html_path=report,
                download=download,
                filename=f"{params['report_name'].lower()}",
                mimetype="application/pdf",
                extension="pdf",
                identifier="queryregistration",
                path=self.get_module(),
                class_name=self.class_name(),
                params=params,
            )
            obj.update(
                success=True,
                uuid=task.uuid,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                download=True,
            )
        except Exception as error:
            log.exception(error)
            obj.update(message="{}".format(error))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def generates_docx(self, report, params):
        """
        Parâmetros:
            report:template do relatório
            params: Parâmetros pertinentes ao relatório
                params: {
                    outfile,
                    report_name,
                    name,
                    identifier
                    periodo
                    output_format
                }
        """

        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            task = Task.start(
                create_docx_task,
                f"Gerando {params['report_name']}",
                success=f"""<p>{params['report_name']} gerado com sucessso.
                <a href="/athenas/MPMTReports/download_file/?uuid=%(uuid)s" target="_blank">Download</a>.
                </p>""",
                user=get_current_user().pk,
                html_path=report,
                download=True,
                filename=params["report_name"].lower(),
                mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                extension="docx",
                identifier=params["identifier"],
                path=self.get_module(),
                class_name=self.class_name(),
                params=params,
            )
            obj.update(
                success=True,
                uuid=task.uuid,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                download=True,
            )
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def download_file(self, *args):
        """
        Método responsável por fazer o download do arquivo do relatório
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
                task.data = ""
                task.save()
                os.unlink(file)
            else:
                self.response = HttpResponseNotFound(
                    "<h1>Arquivo não encontrado ou já baixado.</h1>"
                )
        except Exception as error:
            log.exception(error)
            self.response = HttpResponseBadRequest(
                "<h1>Erro ao Carregar o Relatório.</h1>"
            )

    def generates_csv(self, report, params, download=False):
        """
        Função responsável por iniciar a task de construção de relatório em CSV.

        Parâmetros:
            params: Parâmetros pertinentes ao relatório
                # mandar como **kwargs
                params: {
                    outfile: 'resumo-de-evento-por-consignatario-folha-' + description,
                    report_name: 'Resumo de Evento - por Consignatário',
                    folha: payroll,
                    plano: plan,
                    employee_type: employee_type
                }
            keys: Parâmetros contendo lista de strings, referente aos nomes dos headers(cabeçalhos) da planilha
                list: [
                    'Primeiro Cabeçalho', 'Segundo Cabeçalho'
                ]
        """

        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            task = Task.start(
                report_csv,
                f"Gerando {params['report_name']}",
                success=f"""<p>{params['report_name']} gerado com sucessso.
                <a href="/athenas/MPMTReports/download_file/?uuid=%(uuid)s" target="_blank">Download</a>.
                </p>""",
                user=get_current_user().pk,
                html_path=report,
                download=download,
                filename=f"{params['report_name'].lower()}",
                mimetype="text/csv",
                extension="csv",
                identifier="queryregistration",
                path=self.get_module(),
                class_name=self.class_name(),
                params=params,
            )
            obj.update(
                success=True,
                uuid=task.uuid,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                download=True,
            )
        except Exception as error:
            log.exception(error)
            obj.update(message="{}".format(error))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def marker(self, *args):
        try:
            task = Task.objects.get(
                uuid=self.request.POST.get("uuid"), owner=get_current_user()
            )
            if task.finished is False:
                task.mark_finished()
                task.data = ""
                task.save()
        except Exception as error:
            log.exception(error)
