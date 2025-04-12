from contrib.utils import getLogger
from contrib.utils import get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.rh.ponto.falta import get_data_report

log = getLogger(__name__)
json = get_json_engine()


class RelatorioFalta(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    @login_required("JSON")
    def generate_falta_pdf(self):
        report = "portrait/mpmt/rh/ponto/falta/index.html"
        params = {
            "outfile": "portrait/mpmt/rh/ponto/falta/index.html",
            "report_name": "Relatório de Faltas",
            "servidor": self.request.POST.get("servidor", None),
            "tipo_falta": self.request.POST.get("tipo_falta", None),
            "situacao": self.request.POST.get("situacao", None),
            "impacto_financeiro": self.request.POST.get("impacto_financeiro", None),
            "competencia_desconto": self.request.POST.get("competencia_desconto", None),
            "proce_data_inicio": self.request.POST.get("proce_data_inicio", None),
            "proce_data_fim": self.request.POST.get("proce_data_fim", None),
            "falta_data_inicio": self.request.POST.get("falta_data_inicio", None),
            "falta_data_fim": self.request.POST.get("falta_data_fim", None),
            "types_by_possession": self.request.POST.get("types_by_possession", None),
            "output_format": "PDF",
        }

        self.generates_pdf(report, params)

    @login_required("JSON")
    def generate_falta_csv(self, *args):
        report = ""
        params = {
            "report_name": "Relatório de Faltas",
            "servidor": self.request.POST.get("servidor", None),
            "tipo_falta": self.request.POST.get("tipo_falta", None),
            "situacao": self.request.POST.get("situacao", None),
            "impacto_financeiro": self.request.POST.get("impacto_financeiro", None),
            "competencia_desconto": self.request.POST.get("competencia_desconto", None),
            "proce_data_inicio": self.request.POST.get("proce_data_inicio", None),
            "proce_data_fim": self.request.POST.get("proce_data_fim", None),
            "falta_data_inicio": self.request.POST.get("falta_data_inicio", None),
            "falta_data_fim": self.request.POST.get("falta_data_fim", None),
            "types_by_possession": self.request.POST.get("types_by_possession", None),
            "output_format": "CSV",
        }
        try:
            self.generates_csv(report, params)
        except Exception as e:
            log.error(f"ERRO {e}")
