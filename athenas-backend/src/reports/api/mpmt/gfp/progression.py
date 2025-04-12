from contrib.utils import getLogger
from contrib.utils import get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.gfp.progresssion import get_data_report, get_data

log = getLogger(__name__)
json = get_json_engine()


class ProgressionMoveReport(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.reports.Lista")')

    @login_required("JSON")
    def generate_progression_move_report(self, *args):
        """
        Função para gerar relatório de progressões
        """
        obj = {"success": False, "message": "Nada foi realizado!"}
        try:
            output_format = self.request.POST.get("output_format", "PDF")
            report = "portrait/mpmt/gfp/progression/template.html"
            params = {
                "report_name": self.request.POST.get("title", None),
                "month": self.request.POST.get("month", None),
                "year": self.request.POST.get("year", None),
                "output_format": output_format,
                "progressed": False,
            }

        except Exception as err:
            log.error(err)
        try:
            if output_format == "PDF":
                self.generates_pdf(report, params)
            if output_format == "XLS":
                self.generates_xls(report, params)
        except Exception as err:
            log.error(f"ERRO {err}")
            obj.update({"message": "Houve um erro ao gerar o relatório."})

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))

    @login_required("JSON")
    def generate_progressed_move_report(self, *args):
        """
        Função para gerar relatório de progredidos no mês
        """
        obj = {"success": False, "message": "Nada foi realizado!"}
        try:
            output_format = self.request.POST.get("output_format", "PDF")
            report = "portrait/mpmt/gfp/progression/template.html"
            params = {
                "report_name": self.request.POST.get("title", None),
                "month": self.request.POST.get("month", None),
                "year": self.request.POST.get("year", None),
                "progressed": True,
                "output_format": output_format,
            }

        except Exception as err:
            log.error(err)
        try:
            if output_format == "PDF":
                self.generates_pdf(report, params)
            if output_format == "XLS":
                self.generates_xls(report, params)
        except Exception as err:
            log.error(f"ERRO {err}")
            obj.update({"message": "Houve um erro ao gerar o relatório."})

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))


class RelatorioProrrogacoes(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data(params)

    @login_required("JSON")
    def gerar_relatorio_prorrogacoes(self, *args):
        """
        Função para gerar relatório de prorrogações
        """
        obj = {"success": False, "message": "Nada foi realizado!"}
        try:
            output_format = self.request.POST.get("output_format", "PDF")
            relatorio = "portrait/mpmt/gfp/progression/prorrogacoes.html"
            params = {
                "title": self.request.POST.get("title", None),
                "report_name": "Relatório de Prorrogações",
                "progressao": self.request.POST.getlist("progressoes", None),
                "output_format": output_format,
            }

        except Exception as err:
            log.error(err)
        try:
            if output_format == "PDF":
                self.generates_pdf(relatorio, params)
        except Exception as err:
            log.error(f"ERRO {err}")
            obj.update({"message": "Houve um erro ao gerar o relatório."})

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))
