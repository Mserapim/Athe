from contrib.utils import getLogger, get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.anotacao_pessoal.anotacao.anotacao_pessoal import get_data_report

log = getLogger(__name__)
json = get_json_engine()


class AnotacaoPessoalRelatorio(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    @login_required("JSON")
    def generate_report(self, *args):
        filtro_txt = self.request.POST.get("filtro_txt", None)
        filtro_txt = None if filtro_txt in ["", "0", None] else filtro_txt

        tipos_anotacao = self.request.POST.getlist("tipos_anotacao", None)
        tipos_anotacao = (
            None if tipos_anotacao[0] in ["", "0", None] else tipos_anotacao
        )

        tipos_documentos = self.request.POST.getlist("tipos_documentos", None)
        tipos_documentos = (
            None
            if tipos_documentos and tipos_documentos[0] in ["", "0", None]
            else tipos_documentos
        )

        try:
            report = "portrait/mpmt/anotacao_pessoal/anotacao/template.html"
            params = {
                "outfile": report,
                "report_name": "Relatório de Anotações Pessoais",
                "servidor": self.request.POST.get("servidor", None),
                "filtro_txt": filtro_txt,
                "tipos_anotacao": tipos_anotacao,
                "tipos_documentos": tipos_documentos,
                "name": "Relatório de Anotações Pessoais",
                "output_format": "PDF",
            }
        except Exception as e:
            log.error(e)
        try:
            self.generates_pdf(report, params)
        except Exception as e:
            log.error(f"Erro ao gerar o Relatório de Teletrabalho: {e}")
