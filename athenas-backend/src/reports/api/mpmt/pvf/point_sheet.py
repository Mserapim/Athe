import json as js
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user, getLogger, get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.pvf.point_sheet import get_data_report
from rh.models import Servidor

log = getLogger(__name__)
json = get_json_engine()


class PointSheetCheckReport(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.reports.PointSheetReport")')

    def validate_permission_report(self):
        if (
            not Servidor.objects.filter(pk=employee_from_user(get_current_user()).pk)
            .first()
            .subordinados.all()
            .exists()
        ):
            raise Exception(
                "Não foram localizadas folhas ponto sob sua resposabilidade."
            )

    def validate_reference(self):
        competence = self.request.POST.get("competence", None)
        if "/" not in competence:
            raise Exception(
                "A competência deve possuir o formato MM/AAAA, sendo o 'mês'+'/'+'ano'. Ex.: 01/2022."
            )
        month, year = competence.split("/")
        if len(month) != 2 or len(year) != 4:
            raise Exception(
                "A competência deve possuir o formato MM/AAAA, sendo dois dígitos para mês e quatro dígitos para o ano. Ex.: 01/2022."
            )

    def validate(self):
        self.validate_permission_report()
        self.validate_reference()

    @login_required("JSON")
    def generate_point_sheet_xls(self, *args):
        try:
            self.validate()
            report = ""
            params = {
                "report_name": "Relatório de Folhas Ponto Entregues",
                "competence": self.request.POST.get("competence", None),
                "employee": employee_from_user(get_current_user()).pk,
                "output_format": "XLS",
            }

            self.generates_xls(report, params)
        except Exception as e:
            obj = {"success": False, "message": str(e)}
            self.response["content-type"] = "text/javascript"
            self.response.write(js.dumps(obj))
            log.error(f"ERRO: {e}")
