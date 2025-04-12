import json as js
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user, getLogger, get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.pvf.shiftcontrol import get_data_report

log = getLogger(__name__)
json = get_json_engine()


class ShiftControlReport(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.reports.ShiftControlReport")')

    @login_required("JSON")
    def generate_shift_manager_pdf(self, *args):
        try:
            report = "portrait/mpmt/pvf/shiftmanger/template.html"
            params = {
                "outfile": "portrait/mpmt/pvf/shiftmanger/template.html",
                "report_name": "Escala de Plantões Servidores",
                "competence": self.request.POST.get("competence", None),
                "workplace": self.request.POST.get("workplace", None),
                "employee": self.request.POST.get("employee", None),
                "name": "Escala de Plantões Servidores",
                "output_format": "PDF",
            }
        except Exception as e:
            log.error(e)
        try:
            self.generates_pdf(report, params)
        except Exception as e:
            log.error(f"ERRO {e}")
