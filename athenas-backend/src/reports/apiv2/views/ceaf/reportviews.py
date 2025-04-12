from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework import status

from reports.data.mpmt.ceaf.capacitation.capacitation import get_data_report

from engine.mq.models import Task
from contrib.middleware import get_current_user, set_current_user
from rh.models import Servidor
from ceaf.models import Participant

from reports.apiv2.views.reportbaseviews import ReportBaseView

from contrib.utils import getLogger

log = getLogger(__name__)


class CapacitacaoRelatorioView(ReportBaseView):
    """
    View para realizar o download do relatório de aprovadores
    """

    permission_classes = [IsAuthenticated]

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def gerar_relatorio(self, extensao):
        log.info(extensao)
        task = None
        pk_participante = self.request.POST.get("pk_participante", None)
        participante = (
            Participant.objects.get(pk=pk_participante) if pk_participante else None
        )
        if extensao == "PDF" or extensao == None:
            relatorio = "portrait/mpmt/ceaf/capacitation/index.html"
            params = {
                "outfile": "portrait/mpmt/ceaf/capacitation/index.html",
                "report_name": "Relatório-Sintetizado-de-Capacitações",
                "start_matricula": self.request.POST.get("matricula_inicial", None),
                "end_matricula": self.request.POST.get("matricula_final", None),
                "type_by_possession": self.request.POST.get("tipo_posse", None),
                "capacitation": self.request.POST.get("capacitacao", None),
                "end_competence": self.request.POST.get("competencia_final", None),
                "start_competence": self.request.POST.get("competencia_inicial", None),
                "name": participante.name if participante else None,
                "output_format": "PDF",
                "notificar": self.request.POST.get("notificar", False),
            }
            task = self.generates_pdf(relatorio, params)

        elif extensao == "XLS":
            relatorio = ""
            params = {
                "outfile": "portrait/mpmt/ceaf/capacitation/index.html",
                "report_name": "Relatório-Sintetizado-de-Capacitações",
                "start_matricula": self.request.POST.get("matricula_inicial", None),
                "end_matricula": self.request.POST.get("matricula_final", None),
                "type_by_possession": self.request.POST.get("tipo_posse", None),
                "capacitation": self.request.POST.get("capacitacao", None),
                "end_competence": self.request.POST.get("competencia_final", None),
                "start_competence": self.request.POST.get("competencia_inicial", None),
                "name": participante.name if participante else None,
                "output_format": "XLS",
                "notificar": self.request.POST.get("notificar", False),
            }
            task = self.generates_xls(relatorio, params)

        return task

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "matricula_inicial": {"type": "integer"},
                    "matricula_final": {"type": "integer"},
                    "tipo_posse": {"type": "string"},
                    "capacitacao": {"type": "integer"},
                    "competencia_inicial": {"type": "integer"},
                    "competencia_final": {"type": "integer"},
                    "pk_participante": {"type": "integer"},
                    "tipo_relatorio": {"type": "string"},
                    "extensao": {"type": "string"},
                    "notificar": {"type": "bool"},
                },
            },
        },
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            extensao = request.data.get("extensao", None)

            if extensao:
                extensao = extensao.upper()

            task = self.gerar_relatorio(extensao)
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
