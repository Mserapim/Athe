import json as js

from contrib.utils import getLogger
from contrib.utils import get_json_engine
from contrib.decorator import login_required
from reports.api.base_reports import MPMTReports
from reports.data.mpmt.gfp.cubo import get_data_report
from standard.models import Choice

log = getLogger(__name__)
json = get_json_engine()


class CuboReport(MPMTReports):

    @classmethod
    def get_context_data(self, params):
        return get_data_report(params)

    def json(self, *args):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.reports.Cubo")')

    def employee_type_by_possessions(self, *args):
        """
        Function to return a list of type_by_possessions to filter the report
        """
        result = {
            "success": False,
            "message": "Nothing made yet.",
            "count": 0,
            "collection": [],
        }

        try:
            types_by_possession = Choice.objects.filter(
                app_label="rh", name="CLASSIF_EMPLOYEE_BY_POSSESSION", active=True
            )
        except Exception as error:
            result.update(message=str(error))
        else:
            result.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=types_by_possession.count(),
                collection=[
                    {"value": tp.cvalue, "description": str(tp.label)}
                    for tp in types_by_possession
                ],
            )

        self.response["content-type"] = "text/json"
        self.response.write(js.dumps(result))

    @login_required("JSON")
    def generate_cubo_csv(self, *args):
        """
        Function to generate Cubo's Report
        """
        if not self.request.POST.get(
            "end_competence", None
        ) or not self.request.POST.get("start_competence", None):
            obj = {
                "success": False,
                "message": "Escolha uma data de início e data de fim de competência",
            }

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))
        else:
            try:
                report = ""
                params = {
                    "report_name": "Cubo - Relatório Salarial",
                    "end_competence": self.request.POST.get("end_competence", None),
                    "start_competence": self.request.POST.get("start_competence", None),
                    "active": self.request.POST.get("active", None),
                    "types_by_possession": self.request.POST.get(
                        "types_by_possession", None
                    ),
                    "type_report": int(self.request.POST.get("type_report", None)),
                    "output_format": "CSV",
                }

            except Exception as error:
                log.error(error)
            try:
                self.generates_csv(report, params)
            except Exception as error:
                log.error(f"ERRO {error}")
