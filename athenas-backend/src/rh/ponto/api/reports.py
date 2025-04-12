import json as js

from django.conf import settings

from contrib.controller import DefaultController
from contrib.decorator import login_required
from contrib.utils import get_json_engine, getLogger

from reports.api.mpmt.ponto.falta import RelatorioFalta
from standard.models import Choice

json = get_json_engine()
log = getLogger(__name__)


class PONTRelatorioFalta(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.falta.RelatorioWindow")')

    def employee_type_by_possessions(self, args=[]):
        result = {
            "success": False,
            "message": "Nothing made yet.",
            "count": 0,
            "collection": [],
        }

        try:
            types_by_possession = Choice.objects.filter(
                app_label="rh", name="CLASSIF_EMPLOYEE_BY_POSSESSION", active=True
            ).exclude(
                cvalue__in=[
                    "MCM",
                    "MEC",
                    "TCR",
                    "CTR",
                    "SAP",
                    "MAP",
                    "RFC",
                    "EFC",
                    "JCA",
                    "XXX",
                    "MBR2",
                    "MEL2",
                    "MCM2",
                    "MEC2",
                    "MAP2",
                    "APO",
                    "BFP",
                    "REX",
                    "COE",
                ]
            )
        except Exception as e:
            result.update(message=str(e))
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

    def generate_report_pdf(self, *args):
        RelatorioFalta(self.request, self.response).generate_falta_pdf()

    def generate_report_csv(self, *args):
        RelatorioFalta(self.request, self.response).generate_falta_csv()
