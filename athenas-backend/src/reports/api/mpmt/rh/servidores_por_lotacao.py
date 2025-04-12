from contrib.utils import getLogger, get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.rh.servidores_por_lotacao import get_data_report
from contrib.middleware import get_current_user
from engine.mq.models import Task
from reports.tasks import criar_task_docx, criar_task_servidores_lotacao

log = getLogger(__name__)
json = get_json_engine()


class ServidoresPorLotacaoRelatorio(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    @login_required("JSON")
    def generate_report(self, *args):
        tipo = self.request.POST.get("tipo")
        try:
            report = "portrait/mpmt/rh/servidores_por_lotacao/template.html"
            nome = "Servidores por Lotação"
            params = {
                "outfile": report,
                "report_name": nome,
                "name": nome,
                "output_format": tipo,
                "identifier": "relatorio-servidores-lotacao",
            }
        except Exception as e:
            log.error(e)
        try:
            if tipo == "PDF":
                self.generates_pdf(report, params)
            elif tipo == "DOCX":
                report = "portrait/mpmt/rh/servidores_por_lotacao/template_docx.html"
                params["outfile"] = report
                self.gerar_docx(report, params)
            elif tipo == "XLSX":
                self.gerar_xlsx(report, params)
        except Exception as e:
            log.error(
                f"Erro ao gerar o Relatório {tipo} de Servidores Por Lotação: {e}"
            )

    def gerar_docx(self, report, params):
        """
        Parâmetros:
            report:template do relatório
            params: Parâmetros pertinentes ao relatório
                params: {
                    outfile,
                    report_name,
                    name,
                    identifier
                    periodo
                    output_format
                }
        """

        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            task = Task.start(
                criar_task_docx,
                f"Gerando {params['report_name']}",
                success=f"""<p>{params['report_name']} gerado com sucessso.
                <a href="/athenas/MPMTReports/download_file/?uuid=%(uuid)s">Download</a>.
                </p>""",
                user=get_current_user().pk,
                html_path=report,
                download=True,
                filename=params["report_name"].lower(),
                mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                extension="docx",
                identifier=params["identifier"],
                path=self.get_module(),
                class_name=self.class_name(),
                params=params,
            )
            obj.update(
                success=True,
                uuid=task.uuid,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                download=True,
            )
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def gerar_xlsx(self, report, params):
        """
        Parâmetros:
            report:template do relatório
            params: Parâmetros pertinentes ao relatório
                params: {
                    outfile,
                    report_name,
                    name,
                    identifier
                    periodo
                    output_format
                }
        """

        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            task = Task.start(
                criar_task_servidores_lotacao,
                f"Gerando {params['report_name']}",
                success=f"""<p>{params['report_name']} gerado com sucessso.
                <a href="/athenas/MPMTReports/download_file/?uuid=%(uuid)s">Download</a>.
                </p>""",
                user=get_current_user().pk,
                html_path=report,
                download=True,
                filename=params["report_name"].lower(),
                mimetype="application/vnd.ms-excel",
                extension="xlsx",
                identifier="registration",
                path=self.get_module(),
                class_name=self.class_name(),
                params=params,
            )
            obj.update(
                success=True,
                uuid=task.uuid,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
                download=True,
            )
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
