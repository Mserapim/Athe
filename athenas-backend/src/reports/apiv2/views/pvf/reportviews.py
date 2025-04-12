import base64
from datetime import datetime
from ged.models import Arquivo
from rest_framework.response import Response
from contrib.utils import employee_from_user, getLogger
from drf_spectacular.utils import extend_schema
from contrib.middleware import get_current_user, set_current_user
from reports.apiv2.views.reportbaseviews import ReportBaseView
from rest_framework.views import APIView
from rh.gfp.tasks import get_cedula_c
from rh.models import Lotacao, Servidor
from rh.pvf.api.pvfcalendar.pvfcalendar import calendar_report
from rh.pvf.apiv2.utils.report import paycheck_list
from rest_framework.permissions import IsAuthenticated
from engine.mq.models import Task
from rh.pvf.models import SendingTelework
from rh.pvf.tasks import folha_ponto_relatorio, point_sheet_report
from rest_framework import status
from rh.registerpoint.utils.ponto import inicio_fim_competencia


log = getLogger(__name__)


class PVFReportEmployeeScaleView(ReportBaseView):
    """
    View para realizar o download da escala de plantões servidores
    """

    @classmethod
    def get_context_data(self, params):
        from reports.data.mpmt.pvf.shiftcontrol import get_data_report

        return get_data_report(params)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "competence": {"type": "integer"},
                    "workplace_id": {"type": "integer"},
                    "employee_id": {"type": "integer"},
                    "notificar": {"type": "bool"},
                    "tipo_plantao": {"type": "integer"},
                    "comarcas": {"type": "array", "items": {"type": "integer"}},
                },
            },
        },
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            report = "portrait/mpmt/pvf/shiftmanger/template.html"
            params = {
                "outfile": "portrait/mpmt/pvf/shiftmanger/template.html",
                "report_name": "Escala de Plantões Servidores",
                "competence": request.data.get("competence", None),
                "workplace": request.data.get("workplace_id", None),
                "employee": request.data.get("employee_id", None),
                "tipo_plantao": request.data.get("tipo_plantao", None),
                "comarcas": request.data.get("comarcas", None),
                "data_inicio": request.data.get("inicio", None),
                "data_fim": request.data.get("fim", None),
                "name": "Escala de Plantões Servidores",
                "output_format": "PDF",
                "notificar": request.data.get("notificar", False),
            }
            task = self.generates_pdf(report, params)
            obj.update(
                success=True,
                uuid=task.uuid,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            )
            return Response(obj, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(f"ERRO {e}")
            obj.update(
                success=False,
                message=str(e),
            )
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)


class PVFRelatorioAprovadoresView(ReportBaseView):
    """
    View para realizar o download do relatório de aprovadores
    """

    @classmethod
    def get_context_data(self, params):
        from reports.data.mpmt.pvf.approversvdf import get_data_report

        return get_data_report(params)

    def gerar_relatorio(self, extensao, notificar):
        task = None
        if extensao == "PDF" or extensao == None:
            relatorio = "landescape/mpmt/pvf/approvervdf/template.html"
            params = {
                "outfile": "landescape/mpmt/pvf/approvervdf/template.html",
                "report_name": "Relatório Aprovadores Vida Funcional",
                "name": "Aprovadores Vida Funcional",
                "output_format": "PDF",
                "notificar": notificar,
            }
            task = self.generates_pdf(relatorio, params)

        elif extensao == "XLS":
            relatorio = ""
            params = {
                "report_name": "Relatório Aprovadores Vida Funcional",
                "employee": employee_from_user(get_current_user()).pk,
                "output_format": "XLS",
            }
            task = self.generates_xls(relatorio, params)

        return task

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "extension": {"type": "string"},
                    "notificar": {"type": "bool"},
                },
            },
        },
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            extensao = request.data.get("extension", None)
            notificar = request.data.get("notificar", False)
            task = self.gerar_relatorio(extensao, notificar)
            obj.update(
                success=True,
                uuid=task.uuid,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            )
            return Response(obj, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(f"ERRO {e}")
            obj.update(
                success=False,
                message=str(e),
            )
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)


class PVFReportTeleWorkView(ReportBaseView):

    @classmethod
    def get_context_data(self, params):
        from reports.data.mpmt.pvf.telework import get_data_report

        return get_data_report(params)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "request_id": {"type": "integer"},
                    "notificar": {"type": "bool"},
                },
            },
        },
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            report = "portrait/mpmt/pvf/telework/template.html"
            request_id = request.data.get("send_telework_id", None)
            send_telework = SendingTelework.objects.filter(id=request_id).first()
            employee_id = send_telework.employee.pk
            plan_work_id = send_telework.work_plan.pk
            params = {
                "outfile": "portrait/mpmt/pvf/telework/template.html",
                "report_name": "Relatorio de Teletrabalho",
                "plan_work_id": plan_work_id,
                "employee": employee_id,
                "send_telework_id": request_id,
                "name": "Relatório de Teletrabalho",
                "output_format": "PDF",
                "notificar": request.data.get("notificar", False),
            }
            task = self.generates_pdf(report, params)
            obj.update(
                success=True,
                uuid=task.uuid,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            )
            return Response(obj, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(e)
            obj = {"success": False, "message": str(e)}
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)


class PVFReportDeliveryTimeSheet(ReportBaseView):
    """
    View para realizar o download da entrega de folha ponto
    """

    @classmethod
    def get_context_data(self, params):
        from reports.data.mpmt.pvf.point_sheet import get_data_report

        return get_data_report(params)

    def validate_permission_report(self):
        if (
            not Servidor.objects.filter(pk=employee_from_user(get_current_user()).pk)
            .first()
            .subordinados.all()
            .exists()
        ):
            raise Exception(
                "Não foram localizadas folhas ponto sob sua resposabilidade."
            )

    def validate_reference(self, competence):
        if "/" not in competence:
            raise Exception(
                "A competência deve possuir o formato MM/AAAA, sendo o 'mês'+'/'+'ano'. Ex.: 01/2022."
            )
        month, year = competence.split("/")
        if len(month) != 2 or len(year) != 4:
            raise Exception(
                "A competência deve possuir o formato MM/AAAA, sendo dois dígitos para mês e quatro dígitos para o ano. Ex.: 01/2022."
            )

    def validate(self, competence):
        self.validate_permission_report()
        self.validate_reference(competence)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"competence": {"type": "string"}},
            },
        },
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            competence = request.data.get("competence", None)
            self.validate(competence)
            report = ""
            params = {
                "report_name": "Relatório de Folhas Ponto Entregues",
                "competence": competence,
                "employee": employee_from_user(request.user).pk,
                "output_format": "XLS",
                "notificar": request.data.get("notificar", False),
            }
            task = self.generates_xls(report, params)
            obj.update(
                success=True,
                uuid=task.uuid,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            )
            return Response(obj, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(e)
            obj.update({"success": False, "message": str(e)})
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)


class PVFReportPointSheetView(APIView):
    """
    View para realizar o download do folha ponto
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "month": {"type": "integer"},
                    "year": {"type": "integer"},
                    "employee_id": {"type": "integer"},
                },
            },
        },
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {"success": False, "message": "Arquivo não econtrado"}
        month = request.data.get("month")
        year = request.data.get("year")
        employee_id = request.data.get("employee_id")
        user = request.user.pk
        path = "pointsheet/template.html"
        try:
            if employee_id:
                user = Servidor.objects.get(pk=employee_id).user.pk
            task = Task.start(
                point_sheet_report,
                f"Gerando Relatório",
                success="",
                user=user,
                month=month,
                year=year,
                html_path=path,
                origem_apiv2=True,
            )
            obj.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                uuid=task.uuid,
            )
            return Response(obj, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(e)
            obj.update(message="{}".format(e))
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)


class PVFReportCalendarView(APIView):
    """
    View para realizar o download da agenda
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "month": {"type": "integer"},
                    "year": {"type": "integer"},
                    "type_report": {"type": "integer"},
                    "team_id": {"type": "integer"},
                },
            },
        },
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        employee = Servidor.objects.get(user=request.user)
        month = request.data.get("month")
        year = request.data.get("year")
        type_report = request.data.get("type_report")
        team = request.data.get("team_id")
        responsible_workplaces = Lotacao.objects.filter(responsavel=employee.id)
        try:
            task = Task(owner=request.user)
            task.save()
            calendar_report(
                task,
                f"Gerando Agenda ...",
                success=f"""<p> Agenda...</p>""",
                user=request.user.pk,
                month=month,
                year=year,
                calendar_type=int(type_report),
                team=int(team),
                responsible_workplaces=responsible_workplaces,
                origem_apiv2=True,
            )
            obj.update(
                success=True,
                message="Aguarde o sistema fará o download do agenda solicitada.",
                uuid=task.uuid,
            )
            return Response(obj, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(e)
            obj.update(message="{}".format(e))
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)


class PVFPayCheckView(ReportBaseView):
    """
    View para realizar o download do contracheque
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "month": {"type": "integer"},
                    "year": {"type": "integer"},
                    "type": {"type": "integer"},
                },
            },
        },
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {
            "success": False,
            "message": "Nada feito ainda!",
        }
        try:
            employee = Servidor.objects.get(user=self.request.user)
            month = request.data.get("month")
            year = request.data.get("year")
            type_payroll = request.data.get("type")
            paychecks = paycheck_list(month, year, type_payroll, employee)
            report = "/to/mpe/gfp/paycheck_by_id"
            report_name = (
                "Contra-cheque"
                + " - "
                + str(type_payroll)
                + " - "
                + str(month)
                + " - "
                + str(year)
            )
            params = {
                "outfile": "contracheque"
                + "-"
                + str(type_payroll)
                + "-"
                + str(month)
                + "-"
                + str(year),
                "contracheque": paychecks,
                "admin": 1,
            }
            task = self.gerador_relatorio_jasper(
                params, report, report_name, output="PDF"
            )  # Chama a tarefa assíncrona diretamente
            obj.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                uuid=task.uuid,
            )
            return Response(obj, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(e)
            obj.update(message="{}".format(e))
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)


class PVFFichaFinanceiraView(ReportBaseView):
    """
    View para realizar o download da ficha financeira
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "start_year": {"type": "integer"},
                    "end_year": {"type": "integer"},
                },
            },
        },
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {
            "success": False,
            "message": "Nada feito ainda!",
        }
        try:
            servidor = Servidor.objects.get(user=self.request.user)
            ano_inicial = request.data.get("start_year")
            ano_final = request.data.get("end_year")
            nome = servidor.pessoa_fisica.nome
            relatorio = "/to/mpe/gfp/financial_statement"
            relatorio_nome = (
                f"ficha-financeira-${nome}-${ano_inicial}-a-${ano_final}",
            )
            params = {
                "outfile": f"ficha-financeira-${nome}-${ano_inicial}-a-${ano_final}",
                "servidor": servidor.pk,
                "ano_inicial": ano_inicial,
                "ano_final": ano_final,
            }
            task = self.gerador_relatorio_jasper(
                params, relatorio, relatorio_nome, output="PDF"
            )  # Chama a tarefa assíncrona diretamente
            obj.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                uuid=task.uuid,
            )
            return Response(obj, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(e)
            obj.update(message="{}".format(e))
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)


class PVFInformeRendimentoView(APIView):
    """
    View para realizar o download dos informes de rendimentos
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"year": {"type": "integer"}, "type": {"type": "string"}},
            },
        },
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {"success": False, "message": "Arquivo não econtrado"}

        try:
            ano = int(request.data.get("year"))
            tipo_cedula_c = request.data.get("type", "MPMT")
            retificacao = "R"
            documento = Arquivo.objects.filter(
                user=request.user,
                filename__icontains=f"cedula-c-{retificacao}{ano}-{tipo_cedula_c}",
            ).last()

            if not documento:
                documento = Arquivo.objects.filter(
                    user=request.user,
                    filename__icontains=f"cedula-c-{ano}-{tipo_cedula_c}",
                ).first()

            if documento:
                task = Task.start(
                    get_cedula_c,
                    "cedula-c-report",
                    success="",
                    user=get_current_user().pk,
                    params=[],
                    document_pk=documento.pk,
                    extension="pdf",
                    origem_apiv2=True,
                )
                obj.update(
                    success=True,
                    message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                    uuid=task.uuid,
                )
                return Response(obj, status=status.HTTP_200_OK)
            else:
                obj.update(
                    success=False,
                    message="O servidor ainda não possui Cédula-C cadastrada para a referência informada.",
                )
                return Response(obj, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            log.error(e)
            obj.update(message="{}".format(e))
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)


class PVFReportAnotacaoPessoalView(ReportBaseView):
    """
    View para realizar o download das anotações pessoais do servidor
    """

    @classmethod
    def get_context_data(self, params):
        from reports.data.mpmt.anotacao_pessoal.anotacao.anotacao_pessoal import (
            get_data_report,
        )

        return get_data_report(params)

    def post(self, request):
        set_current_user(request.user)
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            params = request.data
            report = "portrait/mpmt/anotacao_pessoal/anotacao/template.html"
            params = {
                "outfile": "portrait/mpmt/anotacao_pessoal/anotacao/template.html",
                "report_name": "Relatório de Anotações Pessoais",
                "servidor": request.user.servidor.pk,
                "tipos_anotacao": params.get("tipos_anotacao", None),
                "tipos_documento": params.get("tipos_documentos", None),
                "filtro_txt": params.get("filtro_txt", None),
                "name": "Relatório de Anotações Pessoais",
                "output_format": "PDF",
                "notificar": request.data.get("notificar", False),
            }
            task = self.generates_pdf(report, params)
            obj.update(
                success=True,
                uuid=task.uuid,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            )
            return Response(obj, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(f"ERRO {e}")
            obj.update(
                success=False,
                message=str(e),
            )
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)


class ReportContraChequeview(ReportBaseView):
    """
    View para realizar o download
    """

    @classmethod
    def get_context_data(self, params):
        from reports.data.mpmt.gfp.contracheque import get_data_report

        return get_data_report(params)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "month": {"type": "integer"},
                    "year": {"type": "integer"},
                    "type": {"type": "integer"},
                    "notificar": {"type": "bool"},
                },
            },
        },
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            report = "portrait/mpmt/gfp/contracheque/template.html"
            params = {
                "outfile": "portrait/mpmt/gfp/contracheque/template.html",
                "report_name": "Escala de Plantões Servidores",
                "mes": request.data.get("month", None),
                "ano": request.data.get("year", None),
                "tipo_folha": request.data.get("type", None),
                "servidor": request.user.servidor.pk,
                "name": "Contracheque",
                "output_format": "PDF",
                "notificar": request.data.get("notificar", False),
            }
            task = self.generates_pdf(report, params)
            obj.update(
                success=True,
                uuid=task.uuid,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            )
            return Response(obj, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(f"ERRO {e}")
            obj.update(
                success=False,
                message=str(e),
            )
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)


class PVFRelatorioFolhaPontoView(ReportBaseView):
    """
    View para gerar o relatório de folha ponto
    """

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "integer",
                        "description": "ID do servidor para o qual o relatório será gerado.",
                    },
                    "inicio": {
                        "type": "string",
                        "format": "date",
                        "description": "Data inicial do período do relatório no formato YYYY-MM-DD.",
                    },
                    "fim": {
                        "type": "string",
                        "format": "date",
                        "description": "Data final do período do relatório no formato YYYY-MM-DD.",
                    },
                    "month": {
                        "type": "integer",
                        "description": "Mês de competência para o relatório (1 a 12).",
                    },
                    "year": {
                        "type": "integer",
                        "description": "Ano de competência para o relatório.",
                    },
                    "tipos_dia": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Lista de tipos de dias para filtrar (ex.: feriados, faltas).",
                    },
                },
            }
        }
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            servidor_id = request.data.get("employee_id", None)
            inicio = request.data.get("inicio", None)
            fim = request.data.get("fim", None)
            mes = request.data.get("month", None)
            ano = request.data.get("year", None)
            tipos_dia = request.data.get("tipos_dia", [])

            inicio_competencia, fim_competencia = inicio_fim_competencia(mes, ano)
            inicio = (
                datetime.strptime(inicio, "%Y-%m-%d").date()
                if inicio
                else inicio_competencia
            )
            fim = datetime.strptime(fim, "%Y-%m-%d").date() if fim else fim_competencia

            if not servidor_id:
                servidor_id = Servidor.objects.get(user=request.user).id

            path = "pointsheet/template_vdf.html"

            task = Task.start(
                folha_ponto_relatorio,
                f"Gerando Relatório",
                success="",
                servidor_id=servidor_id,
                inicio=inicio.isoformat(),
                fim=fim.isoformat(),
                tipos_dia=tipos_dia,
                html_path=path,
                user_id=request.user.id,
            )
            obj.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                uuid=task.uuid,
            )
            return Response(obj, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(e)
            obj.update(message="{}".format(e))
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)
