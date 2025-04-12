from contrib.utils import getLogger
from contrib.utils import get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.ceaf.capacitation.capacitation import get_data_report

from ceaf.models import Participant

log = getLogger(__name__)
json = get_json_engine()


class CapacitationPDF(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("ceaf.reports.Capacitation")')

    @login_required("JSON")
    def generate_capacitation_pdf(self, *args):
        participant_id = self.request.POST.get("participant_id", None)
        participant = (
            Participant.objects.get(pk=participant_id) if participant_id else None
        )
        try:
            report = "portrait/mpmt/ceaf/capacitation/index.html"
            params = {
                "outfile": "portrait/mpmt/ceaf/capacitation/index.html",
                "report_name": "Relatório-Sintetizado-de-Capacitações",
                "start_matricula": self.request.POST.get("start_matricula", None),
                "end_matricula": self.request.POST.get("end_matricula", None),
                "type_by_possession": self.request.POST.get("type_by_possession", None),
                "capacitation": self.request.POST.get("capacitation", None),
                "end_competence": self.request.POST.get("end_competence", None),
                "start_competence": self.request.POST.get("start_competence", None),
                "name": participant.name if participant else None,
                "output_format": "PDF",
            }
        except Exception as e:
            log.error(e)
        try:
            self.generates_pdf(report, params)
        except Exception as e:
            log.error(f"ERRO {e}")

    @login_required("JSON")
    def generate_capacitation_xls(self, *args):

        try:
            report = "portrait/mpmt/ceaf/capacitation/index.html"
            params = {
                "outfile": "portrait/mpmt/ceaf/capacitation/index.html",
                "report_name": "Relatório-Sintetizado-de-Capacitações",
                "start_matricula": self.request.POST.get("start_matricula", None),
                "end_matricula": self.request.POST.get("end_matricula", None),
                "type_by_possession": self.request.POST.get("type_by_possession", None),
                "capacitation": self.request.POST.get("capacitation", None),
                "end_competence": self.request.POST.get("end_competence", None),
                "start_competence": self.request.POST.get("start_competence", None),
                "name": self.request.POST.get("name", None),
                "output_format": "XLS",
            }
        except Exception as e:
            log.error(e)
        try:
            self.generates_xls(report, params)
        except Exception as e:
            log.error(f"ERRO {e}")
