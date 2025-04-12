from contrib.utils import getLogger
from contrib.utils import get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.lotacionogram.lotacionogram import get_data_report

log = getLogger(__name__)
json = get_json_engine()


class LotacionogramPdf(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    @login_required("JSON")
    def generate_lotacionogram_pdf(self):
        report = "portrait/mpmt/rh/lotacao/lotacionogram/index.html"
        params = {
            "outfile": "portrait/mpmt/rh/lotacao/lotacionogram/index.html",
            "report_name": "Lotacionograma",
            "cargo": self.request.POST.get("cargo", None),
            "lotacao": self.request.POST.get("lotacao", None),
            "nucleo": self.request.POST.get("nucleo", None),
            "municipio": self.request.POST.get("municipio", None),
            "types_by_possession": self.request.POST.get("types_by_possession", None),
            "servidor": self.request.POST.get("servidor", None),
            "comarca": self.request.POST.get("comarca", None),
            "competencia": self.request.POST.get("competencia", None),
            "output_format": "PDF",
        }

        self.generates_pdf(report, params)

    @login_required("JSON")
    def generate_lotacionogram_csv(self, *args):
        report = ""
        params = {
            "report_name": "Lotacionograma",
            "cargo": self.request.POST.get("cargo", None),
            "lotacao": self.request.POST.get("lotacao", None),
            "nucleo": self.request.POST.get("nucleo", None),
            "municipio": self.request.POST.get("municipio", None),
            "types_by_possession": self.request.POST.get("types_by_possession", None),
            "servidor": self.request.POST.get("servidor", None),
            "comarca": self.request.POST.get("comarca", None),
            "competencia": self.request.POST.get("competencia", None),
            "output_format": "CSV",
        }
        try:
            self.generates_csv(report, params)
        except Exception as e:
            log.error(f"ERRO {e}")
