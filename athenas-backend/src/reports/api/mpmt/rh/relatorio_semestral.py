from contrib.utils import getLogger, get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.rh.relatorio_semestral_teletrabalho import get_data_report


log = getLogger(__name__)
json = get_json_engine()


class RelatorioSemestralTeletrabalho(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    @login_required("JSON")
    def generate_report(self, *args):
        formato = self.request.POST.get("formato", "PDF")
        periodo = self.request.POST.get("periodo", None)
        try:
            template = "portrait/mpmt/rh/teletrabalho/relatorio_semestral/template.html"
            template_simplificado = "portrait/mpmt/rh/teletrabalho/relatorio_semestral/template_simplificado.html"
            params = {
                "outfile": "portrait/mpmt/rh/teletrabalho/relatorio_semestral/template.html",
                "report_name": "Relatório Semestral do Teletrabalho",
                "name": "Relatório Semestral do Teletrabalho",
                "identifier": "relatorio-semestral",
                "periodo": periodo,
                "output_format": formato,
            }
        except Exception as e:
            log.error(e)
        try:
            if formato == "PDF":
                self.generates_pdf(template, params)
            elif formato and formato == "DOCX":
                self.generates_docx(template_simplificado, params)
        except Exception as e:
            log.error(f"Erro ao gerar o Relatório de Teletrabalho: {e}")
