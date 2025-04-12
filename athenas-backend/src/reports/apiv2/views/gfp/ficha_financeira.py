from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework import status

from reports.data.mpmt.gfp.ficha_financeira import get_data_report

from engine.mq.models import Task
from contrib.middleware import get_current_user, set_current_user

from reports.apiv2.views.reportbaseviews import ReportBaseView

from contrib.utils import getLogger

log = getLogger(__name__)


class FichaFinanceiraRelatorioView(ReportBaseView):
    """
    View para realizar o download do relatório de aprovadores
    """

    permission_classes = [IsAuthenticated]

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def gerar_relatorio(self):
        task = None

        relatorio = "portrait/mpmt/gfp/ficha_financeira/template.html"
        params = {
            "outfile": "portrait/mpmt/gfp/ficha_financeira/template.html",
            "report_name": "Relatório-Ficha-Financeira",
            "matricula": self.request.data.get("matricula", None),
            "ano_inicial": self.request.data.get("ano_inicial", None),
            "ano_final": self.request.data.get("ano_final", None),
            "output_format": "PDF",
            "notificar": self.request.data.get("notificar", False),
        }
        task = self.generates_pdf(relatorio, params)

        return task

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "matricula": {"type": "integer"},
                    "ano_inicial": {"type": "integer"},
                    "ano_final": {"type": "integer"},
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
