from contrib.utils import getLogger, get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.rh.teletrabalho_competencia import get_data_report

log = getLogger(__name__)
json = get_json_engine()


class TeletrabalhoCompetenciaRelatorio(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    @login_required("JSON")
    def generate_report(self, *args):
        try:
            periodo_ano = int(self.request.POST.get("periodo_ano", None))
            periodo_mes = int(self.request.POST.get("periodo_mes", None))

            report = "portrait/mpmt/rh/teletrabalho/competencia.html"
            params = {
                "outfile": "portrait/mpmt/rh/teletrabalho/competencia.html",
                "report_name": "Relatório de teletrabalhos da competência",
                "periodo_ano": periodo_ano,
                "periodo_mes": periodo_mes,
                "filtro": self.request.POST.get("filtro", None),
                "busca": self.request.POST.get("busca", None),
                "name": "Relatório de teletrabalho por competência",
                "output_format": "PDF",
            }
        except Exception as e:
            log.error(e)
        try:
            self.generates_pdf(report, params)
        except Exception as e:
            log.error(f"Erro ao gerar o Relatório de teletrabalho por competência: {e}")
