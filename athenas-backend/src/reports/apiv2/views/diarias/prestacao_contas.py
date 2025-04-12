from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework import status

from reports.data.mpmt.diarias.prestacao_contas import get_data_report

from engine.mq.models import Task
from contrib.middleware import get_current_user, set_current_user

from reports.apiv2.views.reportbaseviews import ReportBaseView

from contrib.utils import getLogger

log = getLogger(__name__)


class PrestacaoContasDiariasView(ReportBaseView):
    """
    View para realizar o download da Prestação de Contas do Diarias
    """

    permission_classes = [IsAuthenticated]

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def gerar_relatorio(self):
        task = None

        relatorio = "portrait/mpmt/diarias/prestacao_contas/template.html"
        params = {
            "outfile": "portrait/mpmt/diarias/prestacao_contas/template.html",
            "report_name": "Prestação de Contas",
            "id_prestacao": self.request.data.get("id_prestacao", None),
            "output_format": "PDF",
            "notificar": self.request.data.get("notificar", True),
        }
        task = self.generates_pdf(relatorio, params)

        return task

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "id_prestacao": {"type": "integer"},
                    "notificar": {"type": "bool"},
                },
            },
        },
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            task = self.gerar_relatorio()
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
