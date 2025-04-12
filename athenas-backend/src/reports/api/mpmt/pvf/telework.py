from contrib.utils import getLogger, get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.pvf.telework import get_data_report

log = getLogger(__name__)
json = get_json_engine()


class TeleWorkReport(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    @login_required("JSON")
    def generate_report(self, *args):
        try:
            report = "portrait/mpmt/pvf/telework/template.html"
            params = {
                "outfile": "portrait/mpmt/pvf/telework/template.html",
                "report_name": "Relatório de Teletrabalho",
                "plan_work_id": self.request.POST.get("plan_work_id", None),
                "employee": self.request.POST.get("employee", None),
                "send_telework_id": self.request.POST.get("send_telework_id", None),
                "name": "Relatório de Teletrabalho",
                "output_format": "PDF",
            }
        except Exception as e:
            log.error(e)
        try:
            self.generates_pdf(report, params)
        except Exception as e:
            log.error(f"Erro ao gerar o Relatório de Teletrabalho: {e}")
