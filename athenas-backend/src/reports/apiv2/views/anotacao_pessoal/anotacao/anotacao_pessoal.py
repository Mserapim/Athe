from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework import status

from reports.data.mpmt.anotacao_pessoal.anotacao.anotacao_pessoal import get_data_report


from engine.mq.models import Task
from contrib.middleware import get_current_user, set_current_user

from reports.apiv2.views.reportbaseviews import ReportBaseView

from contrib.utils import getLogger

log = getLogger(__name__)


class AnotacaoPessoalRelatorioView(ReportBaseView):
    """
    View para realizar o download do relatório de anotações pessoais
    """

    permission_classes = [IsAuthenticated]

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def processar_lista_post(self, request, campo):
        lista = request.data.get(campo, None)
        # Verifica se a lista é None ou se está vazia
        if not lista or lista == [""]:
            return None

        # Verifica se o primeiro elemento da lista é inválido ('' ou '0' ou None)
        if lista[0] in ["", "0", None]:
            return None

        return lista

    def gerar_relatorio(self):
        task = None

        filtro_txt = self.request.data.get("palavra_chave", None)
        tipos_anotacao = self.processar_lista_post(self.request, "tipos_anotacao")
        tipos_documentos = self.processar_lista_post(self.request, "tipos_documento")

        relatorio = "portrait/mpmt/anotacao_pessoal/anotacao/template.html"
        params = {
            "outfile": "portrait/mpmt/anotacao_pessoal/anotacao/template.html",
            "report_name": "Relatório de Anotações Pessoais",
            "servidor": self.request.data.get("servidor", None),
            "filtro_txt": filtro_txt,
            "tipos_anotacao": tipos_anotacao,
            "tipos_documentos": tipos_documentos,
            "name": "Relatório de Anotações Pessoais",
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
                    "servidor": {"type": "integer"},
                    "palavra_chave": {"type": "string"},
                    "tipos_anotacao": {"type": "integer"},
                    "tipos_documentos": {"type": "integer"},
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
