from contrib.utils import getLogger, get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.rh.teletrabalho import (
    get_data_report,
    get_data_gestor_teletrabalho_report,
)

log = getLogger(__name__)
json = get_json_engine()


class TeletrabalhoRelatorio(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    @login_required("JSON")
    def generate_report(self, *args):
        try:
            report = "portrait/mpmt/rh/teletrabalho/template.html"
            params = {
                "outfile": "portrait/mpmt/rh/teletrabalho/template.html",
                "report_name": "Relatório do Plano de Teletrabalho",
                "mov_teletrabalho": self.request.POST.get("mov_teletrabalho", None),
                "servidor": self.request.POST.get("servidor", None),
                "name": "Relatório do Plano de Teletrabalho",
                "output_format": "PDF",
            }
        except Exception as e:
            log.error(e)
        try:
            self.generates_pdf(report, params)
        except Exception as e:
            log.error(f"Erro ao gerar o Relatório de Teletrabalho: {e}")


class RelatorioGestorTeletrabalho(MPMTReports):
    @classmethod
    def get_context_data(self, params):
        return get_data_gestor_teletrabalho_report(params)

    @login_required("JSON")
    def generate_teletrabalho_pdf(self, *args):
        try:
            report = "portrait/mpmt/rh/teletrabalho/relatorio_gestao/template.html"
            params = {
                "outfile": "portrait/mpmt/rh/teletrabalho/relatorio_gestao/template.html",
                "report_name": "Relatório de Gestão do Teletrabalho",
                "tipo_pedido": self.request.POST.get("tipo_pedido", None),
                "tipo_ato": self.request.POST.get("tipo_ato", None),
                "p_ini_dt_ini": self.request.POST.get("p_ini_dt_ini", None),
                "p_ini_dt_fim": self.request.POST.get("p_ini_dt_fim", None),
                "p_fim_dt_ini": self.request.POST.get("p_fim_dt_ini", None),
                "p_fim_dt_fim": self.request.POST.get("p_fim_dt_fim", None),
                "name": "Relatório de Gestão do Teletrabalho",
                "output_format": "PDF",
            }
        except Exception as e:
            log.error(e)

        try:
            self.generates_pdf(report, params)
        except Exception as e:
            log.error(f"Erro ao gerar o Relatório de Teletrabalho: {e}")

    @login_required("JSON")
    def generate_teletrabalho_csv(self, *args):
        try:
            report = ""
            params = {
                "report_name": "Relatório de Gestão do Teletrabalho",
                "tipo_pedido": self.request.POST.get("tipo_pedido", None),
                "tipo_ato": self.request.POST.get("tipo_ato", None),
                "p_ini_dt_ini": self.request.POST.get("p_ini_dt_ini", None),
                "p_ini_dt_fim": self.request.POST.get("p_ini_dt_fim", None),
                "p_fim_dt_ini": self.request.POST.get("p_fim_dt_ini", None),
                "p_fim_dt_fim": self.request.POST.get("p_fim_dt_fim", None),
                "output_format": "CSV",
            }
        except Exception as e:
            log.error(e)

        try:
            self.generates_csv(report, params)
        except Exception as e:
            log.error(f"Erro ao gerar o Relatório de Teletrabalho: {e}")

    @login_required("JSON")
    def generate_teletrabalho_xls(self, *args):
        try:
            report = "portrait/mpmt/rh/teletrabalho/relatorio_gestao/template.html"
            params = {
                "report_name": "Relatório de Gestão do Teletrabalho",
                "tipo_pedido": self.request.POST.get("tipo_pedido", None),
                "tipo_ato": self.request.POST.get("tipo_ato", None),
                "p_ini_dt_ini": self.request.POST.get("p_ini_dt_ini", None),
                "p_ini_dt_fim": self.request.POST.get("p_ini_dt_fim", None),
                "p_fim_dt_ini": self.request.POST.get("p_fim_dt_ini", None),
                "p_fim_dt_fim": self.request.POST.get("p_fim_dt_fim", None),
                "output_format": "XLS",
            }
        except Exception as e:
            log.error(e)

        try:
            self.generates_xls(report, params)
        except Exception as e:
            log.error(f"Erro ao gerar o Relatório de Teletrabalho: {e}")
