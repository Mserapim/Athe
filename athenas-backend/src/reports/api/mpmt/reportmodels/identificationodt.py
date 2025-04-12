from contrib.utils import getLogger
from contrib.utils import get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.reportmodels.identificationodt import get_data_report
from ged.models import Arquivo
from engine.mq.models import Task
from contrib.middleware import get_current_user
from reports.tasks import write_odt_task

log = getLogger(__name__)
json = get_json_engine()


class IdentificationOdt(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def get_file_path(self, file):
        file = Arquivo.objects.get(pk=file)
        return file.absolute_path

    @login_required("JSON")
    def generate_identification_odt(self, *args):
        try:
            report = self.get_file_path(self.request.POST.get("template", None))
            params = {
                "outfile": self.get_file_path(self.request.POST.get("template", None)),
                "report_name": self.request.POST.get("name", None),
                "output_format": "ODT",
                "employee": self.request.POST.get("employee", None),
            }
        except Exception as e:
            log.error(e)
        try:
            self.generates_odt(report, params)
        except Exception as e:
            log.error(f"ERRO {e}")

    def generates_odt(self, report, params):
        """
        Parâmetros:
            report: Caminho do template do relatório solicitado
                report: '/to/mpe/gfp/employee_by_consignee'

            params: Parâmetros pertinentes ao relatório
                # mandar como **kwargs
                params: {
                    outfile: 'resumo-de-evento-por-consignatario-folha-' + description,
                    report_name: 'Resumo de Evento - por Consignatário',
                    folha: payroll,
                    plano: plan,
                    employee_type: employee_type
                }
        """

        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            task = Task.start(
                write_odt_task,
                f"Gerando {params['report_name']}",
                success=f"""<p>{params['report_name']} gerado com sucessso.
                <a href="/athenas/MPMTReports/download_file/?uuid=%(uuid)s">Download</a>.
                </p>""",
                user=get_current_user().pk,
                html_path=report,
                download=True,
                filename=params["report_name"].lower(),
                mimetype="application/odt",
                extension="odt",
                identifier="modelreport",
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
