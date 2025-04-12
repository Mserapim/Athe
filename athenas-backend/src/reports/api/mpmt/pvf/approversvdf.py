import json as js
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user, getLogger, get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.pvf.approversvdf import get_data_report

log = getLogger(__name__)
json = get_json_engine()


class ApppoverVfdfReport(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.reports.AppoverVdfReport")')

    @login_required("JSON")
    def generate_approver_vdf_pdf(self, *args):
        try:
            report = "landescape/mpmt/pvf/approvervdf/template.html"
            params = {
                "outfile": "landescape/mpmt/pvf/approvervdf/template.html",
                "report_name": "Relatório Aprovadores Vida Funcional",
                "name": "Aprovadores Vida Funcional",
                "output_format": "PDF",
            }
        except Exception as e:
            log.error(e)
        try:
            self.generates_pdf(report, params)
        except Exception as e:
            log.error(f"ERRO {e}")

    @login_required("JSON")
    def generate_approver_vdf_xls(self, *args):
        try:
            report = ""
            params = {
                "report_name": "Relatório Aprovadores Vida Funcional",
                "employee": employee_from_user(get_current_user()).pk,
                "output_format": "XLS",
            }

            self.generates_xls(report, params)
        except Exception as e:
            obj = {"success": False, "message": str(e)}
            self.response["content-type"] = "text/javascript"
            self.response.write(js.dumps(obj))
            log.error(f"ERRO: {e}")
