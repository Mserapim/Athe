from contrib.utils import getLogger
from datetime import datetime
from rh.models import Servidor
import base64
from django.db.models.query_utils import Q
from rh.pvf.utils.point_sheet_data_resume import range_dictfetchall_resume


log = getLogger(__name__)


def get_data_report(params):
    employee = None
    if params.get("employee", None):
        employee = Servidor.objects.get(pk=params.get("employee"))
    start_competence = params.get("start_competence", None)
    end_competence = params.get("end_competence", None)

    data = range_dictfetchall_resume(employee, start_competence, end_competence)

    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    values = {
        "title": params["report_name"],
        "data": data,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
    }
    return values
