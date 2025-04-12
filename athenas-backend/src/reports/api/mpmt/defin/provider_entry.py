from contrib.utils import getLogger
from contrib.utils import get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.defin.provider_entry import get_data_report

log = getLogger(__name__)
json = get_json_engine()


class ProvideEntryReport(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.defin.reports.ProviderEntryReport")')

    @login_required("JSON")
    def generate_provider_entry_pdf(self, *args):
        try:
            report = "portrait/mpmt/ceaf/capacitation/index.html"
            params = {
                "outfile": "portrait/mpmt/ceaf/capacitation/index.html",
                "report_name": "Relatório Prestadores PF",
                "competence": self.request.POST.get("competence", None),
                "output_format": "PDF",
            }
        except Exception as e:
            log.error(e)
        try:
            self.generates_pdf(report, params)
        except Exception as e:
            log.error(f"ERRO {e}")

    @login_required("JSON")
    def generate_provider_entry_xls(self, *args):

        try:
            report = "portrait/mpmt/ceaf/capacitation/index.html"
            log.info(
                self.request.POST.get("competence", None),
            )
            params = {
                "outfile": "portrait/mpmt/ceaf/capacitation/index.html",
                "report_name": "Relatório Prestadores PF",
                "competence": self.request.POST.get("competence", None),
                "output_format": "XLS",
            }

        except Exception as e:
            log.error(e)
        try:
            self.generates_xls(report, params)
        except Exception as e:
            log.error(f"ERRO {e}")
