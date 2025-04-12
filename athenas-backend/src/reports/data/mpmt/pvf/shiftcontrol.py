from contrib.utils import getLogger
from rh.models import Servidor
from datetime import datetime
import base64
from rh.pvf.models import ShiftManager
from rh.models import Lotacao, Servidor
from django.db.models.query_utils import Q


log = getLogger(__name__)


def get_data_report(params):
    workplace = None
    employee = None

    if params["competence"]:
        competence_month, competence_year = params["competence"].split("/")

        shift_managers = ShiftManager.objects.filter(
            Q(start_date__year=competence_year, start_date__month=competence_month)
            | Q(end_date__year=competence_year, end_date__month=competence_month)
        ).order_by("workplace__nome", "start_date")

    elif params["data_inicio"] and params["data_fim"]:
        start_date = datetime.fromisoformat(
            params["data_inicio"].replace("Z", "")
        ).date()
        end_date = datetime.fromisoformat(params["data_fim"].replace("Z", "")).date()
        shift_managers = ShiftManager.objects.filter(
            Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
        ).order_by("workplace__nome", "start_date")

    else:
        shift_managers = ShiftManager.objects.all().order_by(
            "workplace__nome", "start_date"
        )

    if params["workplace"]:
        workplace = Lotacao.objects.get(pk=params["workplace"])
        shift_managers = shift_managers.filter(workplace=workplace)
    if params["employee"]:
        employee = Servidor.objects.get(pk=params["employee"])
        shift_managers = shift_managers.filter(employee=employee)
    if params["tipo_plantao"]:
        shift_managers = shift_managers.filter(type_shift=params["tipo_plantao"])
    if params["comarcas"]:
        comarcas = params.get("comarcas")
        shift_managers = shift_managers.filter(
            employee__servidor_lotacao__lotacao__localidade__id__in=comarcas,
            employee__servidor_lotacao__ativo=True,
            employee__servidor_lotacao__designacao=False,
        )

    shift_managers = [
        sm for sm in shift_managers if sm.get_status not in [5, 7]
    ]  # Indeferido, Cancelado pelo aplicante

    data = {}
    for manager in shift_managers:
        servidor_lotacao = manager.employee.servidor_lotacao.filter(
            ativo=True, designacao=False
        )
        if not data.get(manager.workplace.nome):
            data.update({manager.workplace.nome: []})
            data[manager.workplace.nome].append(
                {
                    "data_inicio": manager.start_date.strftime("%d/%m/%Y"),
                    "data_fim": manager.end_date.strftime("%d/%m/%Y"),
                    "servidor": f"{manager.employee.matricula} : {manager.employee.pessoa_fisica.nome}",
                    "tipo": manager.get_type_shift_display(),
                    "responsavel": manager.owner.pessoa_fisica.nome,
                    "lotacao": (
                        servidor_lotacao.first().lotacao.nome
                        if servidor_lotacao.first()
                        else ""
                    ),
                    "comarca": (
                        servidor_lotacao.first().lotacao.localidade.nome
                        if servidor_lotacao.first()
                        else ""
                    ),
                }
            )
        else:
            data[manager.workplace.nome].append(
                {
                    "data_inicio": manager.start_date.strftime("%d/%m/%Y"),
                    "data_fim": manager.end_date.strftime("%d/%m/%Y"),
                    "servidor": f"{manager.employee.matricula} : {manager.employee.pessoa_fisica.nome}",
                    "tipo": manager.get_type_shift_display(),
                    "responsavel": manager.owner.pessoa_fisica.nome,
                    "lotacao": (
                        servidor_lotacao.first().lotacao.nome
                        if servidor_lotacao.first()
                        else ""
                    ),
                    "comarca": (
                        servidor_lotacao.first().lotacao.localidade.nome
                        if servidor_lotacao.first()
                        else ""
                    ),
                }
            )

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
