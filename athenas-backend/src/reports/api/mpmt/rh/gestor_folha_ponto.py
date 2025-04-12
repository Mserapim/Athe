from contrib.utils import getLogger, get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.rh.ponto.gestor_folhaponto import get_data_report


log = getLogger(__name__)
json = get_json_engine()


class GestorFolhaPonto(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    @login_required("JSON")
    def generate_report(self, *args):
        formato = self.request.POST.get("formato", "PDF")
        status = self.request.POST.get("status")
        notificado = self.request.POST.get("notificado")
        teletrabalho = self.request.POST.get("teletrabalho")
        data = {
            "mes_competencia": self.request.POST.get("mes"),
            "ano_competencia": self.request.POST.get("ano"),
            "status": "todos" if status == "" else status,
            "posses": self.request.POST.get("posses"),
            "notificado": "todos_notificados" if notificado == "" else notificado,
            "teletrabalho": "teletrabalho_nao" if teletrabalho == "" else teletrabalho,
            "keyword": self.request.POST.get("keyword"),
        }
        try:
            template = "landescape/mpmt/rh/folhaponto/template.html"
            params = {
                "outfile": "landescape/mpmt/rh/folhaponto/template.html",
                "report_name": "Relatório Gestor Folha Ponto",
                "name": "Relatório Gestor Folha Ponto",
                "identifier": "gestor-folha-ponto",
                "data": data,
                "output_format": formato,
            }
        except Exception as e:
            log.error(e)
        try:
            if formato == "PDF":
                self.generates_pdf(template, params)
            elif formato and formato == "XLS":
                self.generates_xls(template, params)
            elif formato and formato == "CSV":
                self.generates_csv(template, params)
        except Exception as e:
            log.error(f"Erro ao gerar o relatório: {e}")
