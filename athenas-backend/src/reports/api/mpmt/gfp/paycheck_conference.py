from contrib.utils import getLogger
from contrib.utils import get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.gfp.paycheck_conference import get_data_report
from rh.gfp.models import Folha

log = getLogger(__name__)
json = get_json_engine()


class PaycheckConferenceReport(MPMTReports):
    """
    Classe responsável por gerar o Relatório Conferência de Folha de Pagamento
    """

    @classmethod
    def get_context_data(cls, params):
        """
        Método que retorna as informações de contexto para criação do relatório
        :params params: (dict) Dicionário de parâmentros para filtros do relatório
        :returns: (dict) Dicionário contendo dados para gerar o relatório
        """
        return get_data_report(params)

    @login_required("JSON")
    def generate_paycheck_conference(self, *args):
        """
        Método para criar relatório de Conferência de Folha
        """
        if not self.request.POST.get("previous_payroll", None):
            obj = {
                "success": False,
                "message": """
                    Preencha a Folha anterior no cadastro da Folha de pagamento selecionada
                """,
            }

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))
        else:
            try:
                output_format = self.request.POST.get("output_format", None)
                payroll = Folha.objects.filter(
                    pk=int(self.request.POST.get("payroll", None))
                ).first()
                previous_payroll = Folha.objects.filter(
                    pk=int(self.request.POST.get("previous_payroll", None))
                ).first()
                unify = self.request.POST.get("unify", False)
                params = {
                    "report_name": f"Conferência de Folha {payroll.periodo.mes}-{payroll.periodo.ano} {payroll.tipo_folha} com {previous_payroll.periodo.mes}-{previous_payroll.periodo.ano} {previous_payroll.tipo_folha}",
                    "outfile": "portrait/mpmt/ceaf/capacitation/index.html",
                    "payroll": self.request.POST.get("payroll", None),
                    "previous_payroll": self.request.POST.get("previous_payroll", None),
                    "type_by_possession": self.request.POST.get(
                        "type_by_possession", None
                    ),
                    "unify": True if unify == "on" else False,
                    "output_format": output_format,
                }

            except Exception as error:
                log.error(error)
            try:
                if output_format == "XLS":
                    self.generates_xls(report="", params=params)
                elif output_format == "PDF":
                    self.generates_pdf(
                        report="portrait/mpmt/gfp/paycheck_conference/template.html",
                        params=params,
                    )
                else:
                    raise ValueError("Forneça um formato válido para o relatório")
            except Exception as error:
                log.error(f"ERRO {error}")
