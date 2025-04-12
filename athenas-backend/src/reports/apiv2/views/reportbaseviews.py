import ast
from functools import partial
import os
import base64
from app import settings
from auth.backend import CustomJWTAuthentication
from contrib.base_converter import str_to_bool
from contrib.reports import start_report
from reports.tasks import pdf_task, report_xls, report_xlsx
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from contrib.utils import getLogger, import_from_string
from engine.mq.models import Task
from contrib.middleware import get_current_user
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.decorators import authentication_classes, permission_classes
import json
from django.http import FileResponse


log = getLogger(__name__)


class ReportBaseView(APIView):
    """
    View para gerar o relatório
    """

    permission_classes = [IsAuthenticated]

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

    def gerador_relatorio_jasper(self, params, relatorio, relatorio_nome, output=None):
        """
        Função que chama uma task que gera o relatório de contracheque.
        Args:
        params (dict): Um dicionário contendo os parâmetros necessários para gerar o relatório.
        relatorio (Task): path do jasper para gerar o relatório.
        relatorio_nome (str): O nome do relatório a ser gerado.
        output (str): formato de saída do relatório.
        Returns:
        dict:
        """
        try:
            if not "organ_identifier" in params:
                params["organ_identifier"] = settings.ORGAN_IDENTIFIER
            params["origem_apiv2"] = True

            if getattr(settings, "REPORT_DEFAULT_PATH", None):
                relatorio = "".join(["/", settings.REPORT_DEFAULT_PATH, relatorio])
            task = Task.start(
                start_report,
                report=relatorio,
                report_name=relatorio_nome,
                params=params,
                output_format=output,
                success="",
            )
            return task
        except Exception as e:
            log.error(e)

    def generates_pdf(self, report, params, download=True):
        """
        Função responsável por iniciar a task de construção de relatório em PDF.

        Parâmetros:
            report: Caminho do template do relatório solicitado
                report: '/to/mpe/gfp/employee_by_consignee'

            params: Parâmetros pertinentes ao relatório

        """

        try:
            notificar = params.get("notificar", False)
            task = Task.start(
                pdf_task,
                f"{params['report_name']}",
                success=f"""<a href="/athenas/api/v2/report/download/?uuid=%(uuid)s">Download</a>.""",
                user=get_current_user().pk,
                html_path=report,
                download=download,
                filename=f"{params['report_name'].lower()}",
                mimetype="application/pdf",
                extension="pdf",
                identifier="queryregistration",
                path=self.get_module(),
                class_name=self.class_name(),
                origem_apiv2=True,
                notificar=(
                    notificar if isinstance(notificar, bool) else str_to_bool(notificar)
                ),
                params=params,
            )
            return task
        except Exception as error:
            log.error(str(error))

    def generates_xls(self, report, params, keys=None, download=True):
        """
        Função responsável por iniciar a task de construção de relatório em XLS.

        Parâmetros:
            report: Caminho do template do relatório solicitado
                report: '/to/mpe/gfp/employee_by_consignee'

            params: Parâmetros pertinentes ao relatório

            keys: Parâmetros contendo lista de strings, referente aos nomes dos headers(cabeçalhos) da planilha
                list: [
                    'Primeiro Cabeçalho', 'Segundo Cabeçalho'
                ]
        """
        try:
            notificar = params.get("notificar", False)
            task = Task.start(
                report_xls,
                f"{params['report_name']}",
                success=f"""<a href="/athenas/api/v2/report/download/?uuid=%(uuid)s">Download</a>""",
                user=get_current_user().pk,
                html_path=report,
                download=download,
                filename=f"{params['report_name'].lower()}",
                mimetype="application/vnd.ms-excel",
                extension="xls",
                identifier="registration",
                path=self.get_module(),
                class_name=self.class_name(),
                params=params,
                origem_apiv2=True,
                notificar=(
                    notificar if isinstance(notificar, bool) else str_to_bool(notificar)
                ),
                keys=keys,
            )
            return task
        except Exception as error:
            log.error(error)

    def generates_xlsx(self, report, params, keys=None, download=True):
        """
        Função responsável por iniciar a task de construção de relatório em XLSX.

        Parâmetros:
            report: Caminho do template do relatório solicitado
                report: '/to/mpe/gfp/employee_by_consignee'

            params: Parâmetros pertinentes ao relatório

            keys: Parâmetros contendo dicionário onde a key é o nome do campo e o value é
            referente aos nomes dos headers(cabeçalhos) da planilha
                dict: {
                    'primeiro_cabeçalho': 'Primeiro Cabeçalho',
                    'segundo_cabeçalho': 'SEGUNDO CABEÇALHO'
                }
        """
        try:
            notificar = params.get("notificar", False)
            task = Task.start(
                report_xlsx,
                f"{params['report_name']}",
                success=f"""<a href="/athenas/api/v2/report/download/?uuid=%(uuid)s">Download</a>""",
                user=get_current_user().pk,
                html_path=report,
                download=download,
                filename=f"{params['report_name'].lower()}",
                mimetype="application/vnd.ms-excel",
                extension="xlsx",
                identifier="registration",
                path=self.get_module(),
                class_name=self.class_name(),
                params=params,
                origem_apiv2=True,
                notificar=(
                    notificar if isinstance(notificar, bool) else str_to_bool(notificar)
                ),
                keys=keys,
            )
            return task
        except Exception as error:
            log.error(error)


class ConsultaSituacaoRelatorio(APIView):
    """
    View para consultar se o arquivo está pronto para download.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="uuid", description="uuid da task", type=str),
        ]
    )
    def get(self, request, *args, **kwargs):
        "View para consultar se o arquivo está pronto para download."
        try:
            rst = {}
            task = Task.objects.get(uuid=request.GET.get("uuid"), owner=request.user)
            if task.state == "ready":
                rst.update(
                    {"status": "success", "message": "Relatório gerado com sucesso."}
                )
                return Response(rst, status=status.HTTP_200_OK)
            elif task.state in ["initializing", "progress", "execution"]:
                rst.update(
                    {"status": "processing", "message": "Relatório em processamento."}
                )
                return Response(rst, status=status.HTTP_200_OK)
            elif task.state == "mf-ready":
                rst.update(
                    {"status": "consulted", "message": "Relatório já foi baixado."}
                )
                return Response(rst, status=status.HTTP_200_OK)
            else:
                rst = {"status": "failure", "message": "Erro ao gerar o relatório."}
                return Response(rst, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log.error(e)
            rst.update({"status": "failure", "message": str(e)})
            return Response(rst, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes(import_from_string(settings.AUTHENTICATION_CLASSES_REPORT))
@permission_classes(import_from_string(settings.PERMISSION_CLASSES_REPORT))
class ReportDownloadFile(APIView):
    """
    View para realizar o download do arquivo
    """

    @extend_schema(
        parameters=[
            OpenApiParameter(name="uuid", description="uuid da task", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        "View do download do relatório"
        try:
            rst = {}
            task = Task.objects.get(uuid=request.GET.get("uuid"))
            download = str_to_bool(request.GET.get("download", "true"))
            if task.state == "ready":
                data = ast.literal_eval(task.data)
                file = data.get("file")
                filename = data.get("filename")
                mimetype = data.get("mimetype")
                extension = data.get("extension")
                remove_file = data.get("remove_file", True)
                if extension == "xlsx":
                    task.mark_finished()
                    task.data = ""
                    task.save()
                    return FileResponse(
                        open(file, "rb"),
                        as_attachment=True,
                        filename=f"{filename}.{extension}",
                    )
                response = HttpResponse()
                tp_conteudo = "attachment" if download else mimetype
                response["Content-Disposition"] = (
                    f'{tp_conteudo}; filename="%(filename)s.%(extension)s"'
                    % {"filename": filename, "extension": extension}
                )
                response["Content-Type"] = mimetype
                if os.path.exists(file):
                    with open(file, "rb") as fd:
                        for data in iter(partial(fd.read, 8192), b""):
                            response.write(data)
                        if remove_file:
                            os.unlink(file)
                else:
                    response.write(base64.b64decode(file))
                task.mark_finished()
                task.data = ""
                task.save()
                return response
            else:
                rst = {
                    "status": False,
                    "message": "Relatório não esta pronto ou não foi solicitado.",
                }
                return Response(rst, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback

            trace = traceback.format_exc()
            log.error(trace)
            rst = {"status": False, "message": "Erro ao carregar o relatório."}
            return Response(rst, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes(import_from_string(settings.AUTHENTICATION_CLASSES_REPORT))
@permission_classes(import_from_string(settings.PERMISSION_CLASSES_REPORT))
class PVFDownloadJasperFile(APIView):
    """
    View para realizar o download do arquivo pelo Jasper
    """

    # permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="uuid", description="uuid da task", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        "View do download do relatório"
        cache_path = getattr(settings, "CACHE", {}).get("jreport", None)

        try:
            task = Task.objects.get(
                uuid=request.GET.get("uuid"),
                # owner=request.user
            )

            formats = {
                "PDF": ["application/pdf", "pdf"],
                "CSV": ["text/csv", "csv"],
                "XLS": ["application/vnd.ms-excel", "xls"],
                "ODT": ["application/vnd.oasis.opendocument.text", "odt"],
                "ODS": ["application/vnd.oasis.opendocument.spreadsheet", "ods"],
            }

            mimetype, ext = formats.get(
                request.GET.get("output_format", "PDF"),
                [
                    request.GET.get("output_mimetype", "application/octstream"),
                    request.GET.get("output_extension", "bin"),
                ],
            )
            download = str_to_bool(request.GET.get("download", "true"))
            if task.state == "ready":
                data = json.loads(task.data)
                filename = os.path.join(
                    cache_path, "-".join([data.get("queue"), data.get("outid")])
                )
                params = json.loads(task.params)
                if params.get("params"):
                    outifile = params["params"].get("outfile", "Relatório")
                else:
                    outifile = "Relatório"

                tp_conteudo = "attachment" if download else mimetype
                response = HttpResponse()
                response["Content-Type"] = mimetype
                response["Content-Disposition"] = (
                    f'{tp_conteudo}; filename="%(filename)s.%(extension)s"'
                    % {"filename": outifile, "extension": ext}
                )
                with open(filename, "rb") as fd:
                    for data in iter(partial(fd.read, 8192), b""):
                        response.write(data)

                task.state = "downloaded"
                task.save()
                return response
            else:
                rst = {
                    "status": False,
                    "message": "Relatório não esta pronto ou não foi solicitado.",
                }
                return Response(rst, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log.error(e)
            rst = {"status": False, "message": "Erro ao carregar o relatório."}
            return Response(rst, status=status.HTTP_400_BAD_REQUEST)
