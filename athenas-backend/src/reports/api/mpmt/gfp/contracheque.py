from contrib.utils import getLogger, get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.gfp.contracheque import get_data_report
from rh.gfp.models import ContraCheque

log = getLogger(__name__)
json = get_json_engine()


class RelatorioContracheque(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create(rh.gfp.reports.PayCheckManage")')

    @login_required("JSON")
    def generate_report(self, *args):
        try:
            contracheque_id = self.request.POST.get("paycheck")
            servidor = self.request.POST.get("employee")
            if not servidor:
                servidor = ContraCheque.objects.get(pk=contracheque_id).servidor.pk
            inicio = self.request.POST.get("start")
            fim = self.request.POST.get("end")
            inicio_mes, inicio_ano = [None, None]
            fim_mes, fim_ano = [None, None]
            if inicio:
                inicio_mes, inicio_ano = inicio.split("/")
            if fim:
                fim_mes, fim_ano = fim.split("/")

            report = "portrait/mpmt/gfp/contracheque/template.html"
            params = {
                "outfile": "portrait/mpmt/gfp/contracheque/template.html",
                "report_name": "Contracheque",
                "inicio": inicio,
                "fim": fim,
                "inicio_mes": inicio_mes,
                "inicio_ano": inicio_ano,
                "fim_mes": fim_mes,
                "fim_ano": fim_ano,
                "tipo_folha": self.request.POST.get("type"),
                "contracheque_id": contracheque_id,
                "servidor": servidor,
                "name": "Contracheque",
                "output_format": "PDF",
            }
            self.generates_pdf(report, params)
        except Exception as e:
            log.error(f"Erro ao gerar o Relatório do contracheque: {e}")
