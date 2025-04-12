import json as js
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user, getLogger, get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.pvf.negativepoint import get_data_report

log = getLogger(__name__)
json = get_json_engine()


class NegativeBalancePoint(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.reports.NegativeBalancePoint")')

    @login_required("JSON")
    def generate_negative_balance_pdf(self, *args):
        try:
            report = "portrait/mpmt/pvf/pointsheet/index.html"
            params = {
                "outfile": "portrait/mpmt/pvf/pointsheet/index.html",
                "report_name": "Saldo Negativo Folha Ponto",
                "start_competence": self.request.POST.get("start_competence", None),
                "end_competence": self.request.POST.get("end_competence", None),
                "employee": self.request.POST.get("employee", None),
                "name": "Saldo Negativo Folha Ponto",
                "output_format": "PDF",
            }
        except Exception as e:
            log.error(e)
        try:
            self.generates_pdf(report, params)
        except Exception as e:
            log.error(f"ERRO {e}")
