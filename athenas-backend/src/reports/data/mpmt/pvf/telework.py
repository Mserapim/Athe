from contrib.br import br_month
from contrib.utils import employee_from_user, getLogger
from rh.models import MovimentacaoTeletrabalho, Servidor
from datetime import datetime
import base64
from rh.pvf.models import PortalRequestHistory, SendingTelework, ShiftManager
from rh.models import Lotacao, Servidor
from django.db.models.query_utils import Q


log = getLogger(__name__)


def get_cargo(employee, reference_date):
    effective = None
    commission = None
    possessions = employee.posses

    effectives = possessions.filter(
        Q(data_exercicio__lte=reference_date),
        Q(data_desligamento__gt=reference_date) | Q(data_desligamento__isnull=True),
        quadro__cargo__tipo_lei_cargo="EF",
    )
    if effectives.exists():
        ef = effectives.latest("data_exercicio")
        effective = ef.quadro
    if employee.ativo or (not effective):
        commissions = possessions.filter(
            Q(data_exercicio__lte=reference_date),
            Q(data_desligamento__gt=reference_date) | Q(data_desligamento__isnull=True),
            quadro__cargo__tipo_lei_cargo__in=("CM", "FC"),
        )
        if commissions.exists():
            cm = commissions.latest("data_exercicio")
            commission = cm.quadro
    if not effective and not commission:
        effective = "Não encontrado"
    return str(effective) if effective else str(commission)


def get_data_report(params):
    """
    Função que retorna um dicionário de dados necessários à geração do relatório
    """
    plan_work_id = params["plan_work_id"]
    send_telework_id = params["send_telework_id"]
    employee = params["employee"]

    data = {}
    data_marks = []
    data_history = []

    employee = Servidor.objects.get(pk=employee)
    mov_telework = MovimentacaoTeletrabalho.objects.filter(id=plan_work_id).first()
    send_telework = SendingTelework.objects.filter(id=send_telework_id).first()
    approver = (
        employee_from_user(
            PortalRequestHistory.objects.filter(portal_request=send_telework, action=12)
            .first()
            .user
        )
        if PortalRequestHistory.objects.filter(
            portal_request=send_telework, action=12
        ).exists()
        else mov_telework.aprovador
    )
    mark_requests = send_telework.pvf_request_telework.all()

    for mark in mark_requests:
        data_marks.append(
            {
                "description": mark.mark_plan.descricao,
                "plan_mark": f"{mark.mark_plan.meta} ({mark.mark_plan.get_periodicity_display()})",
                "qnt_completed": mark.total_completed,
                "status": mark.get_mark_situation_display(),
                "observation": mark.observation,
            }
        )

    for history in PortalRequestHistory.objects.filter(portal_request=send_telework):
        data_history.append(
            {
                "date": history.date,
                "group": history.group if history.group else "",
                "action_employee": Servidor.objects.filter(user=history.user).first(),
                "action": history.get_action_display(),
                "observation": history.observation,
            }
        )

    data["name"] = mov_telework.servidor.pessoa_fisica.nome
    data["work_role"] = get_cargo(employee, send_telework.date)
    data["lotation"] = str(employee.workplace_only_active.first().lotacao)
    data["immediate_boss"] = approver
    data["reference_date"] = (
        f"{br_month(send_telework.reference_month)}/{send_telework.reference_year}"
    )
    data["mark_telework"] = data_marks
    data["historicals"] = data_history

    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    values = {
        "title": params["name"],
        "data": data,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
    }
    return values
