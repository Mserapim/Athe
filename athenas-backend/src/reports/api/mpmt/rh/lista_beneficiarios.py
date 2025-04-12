from contrib.utils import getLogger, get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.rh.lista_beneficiarios import get_data_report

log = getLogger(__name__)
json = get_json_engine()


class ListaBeneficiariosRelatorio(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    @login_required("JSON")
    def generate_report(self, *args):

        post_dict = self.request.POST.dict()

        try:
            report = "portrait/mpmt/rh/lista_beneficiarios.html"
            params = {
                "outfile": "portrait/mpmt/rh/lista_beneficiarios.html",
                "report_name": "Relatório Lista de Beneficiarios",
                "ativo": post_dict.get("ativo", None),
                "cargo": post_dict.get("cargo", None),
                "servidor": post_dict.get("servidor", None),
                "tipo_arquivo": post_dict.get("tipo_arquivo", None),
                "paridade_salarial": post_dict.get("paridade_salarial", None),
                "beneficio_integral": post_dict.get("beneficio_integral", None),
                "name": "Relatório Lista de Beneficiarios",
                "output_format": post_dict.get("tipo_arquivo", "PDF"),
            }
        except Exception as e:
            log.error(e)
        try:
            if params["output_format"] == "XLS":
                self.generates_xls(report, params)
            else:
                self.generates_pdf(report, params)
        except Exception as e:
            log.error(f"Erro ao gerar o Relatório de teletrabalho por competência: {e}")
