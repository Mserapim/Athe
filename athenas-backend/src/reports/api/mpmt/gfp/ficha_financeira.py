from contrib.utils import getLogger, get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.gfp.ficha_financeira import get_data_report
from rh.models import Servidor

log = getLogger(__name__)
json = get_json_engine()


class RelatorioFichaFinanceira(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create(rh.gfp.reports.FinancialStatementManage")')

    @login_required("JSON")
    def generate_report(self, *args):
        try:

            servidor_id = self.request.POST.get("servidor_id")
            servidor = Servidor.objects.get(id=servidor_id)

            relatorio = "portrait/mpmt/gfp/ficha_financeira/template.html"
            params = {
                "outfile": "portrait/mpmt/gfp/ficha_financeira/template.html",
                "report_name": "Relatório-Ficha-Financeira",
                "matricula": servidor.matricula,
                "ano_inicial": self.request.POST.get("ano_inicial", None),
                "ano_final": self.request.POST.get("ano_final", None),
                "output_format": "PDF",
            }

            self.generates_pdf(relatorio, params)

        except Exception as e:
            log.error(f"Erro ao gerar o Relatório da Ficha Financeira: {e}")
