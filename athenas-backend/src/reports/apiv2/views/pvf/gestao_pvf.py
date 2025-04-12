from reports.apiv2.views.reportbaseviews import ReportBaseView
from reports.data.mpmt.pvf.gestao_pvf import get_data_report
from contrib.middleware import set_current_user
from rest_framework.response import Response
from rest_framework import status
from contrib.utils import getLogger


log = getLogger(__name__)


class GestaoVDFReportView(ReportBaseView):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def gerar_relatorio(self, extensao):

        relatorio = "landescape/mpmt/pvf/approvervdf/template.html"
        params = {
            "outfile": "landescape/mpmt/pvf/approvervdf/template.html",
            "report_name": "Relatório_Gestão_VDF",
            "name": "Gestão VDF",
            "output_format": "XLSX",
            "notificar": True,
            "usuarios[]": self.request.query_params.getlist("usuarios[]"),
            "tipos_solicitacoes[]": self.request.query_params.getlist(
                "tipos_solicitacoes[]"
            ),
            "situacoes[]": self.request.query_params.getlist("situacoes[]"),
            "categorias[]": self.request.query_params.getlist("categorias[]"),
            "tipos_acoes[]": self.request.query_params.getlist("tipos_acoes[]"),
            "solicitacao_inicio_em": self.request.query_params.get(
                "solicitacao_inicio_em"
            ),
            "solicitacao_fim_em": self.request.query_params.get("solicitacao_fim_em"),
            "acao_inicio_em": self.request.query_params.get("acao_inicio_em"),
            "acao_fim_em": self.request.query_params.get("acao_fim_em"),
            "keyword": self.request.query_params.get("keyword")
            or self.request.query_params.get("palavra_chave"),
            "filtrar_por": self.request.query_params.get("filtrar_por", ""),
        }
        task = self.generates_xlsx(relatorio, params)

        return task

    def get(self, request):
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
