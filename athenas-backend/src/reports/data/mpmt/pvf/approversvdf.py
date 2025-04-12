from contrib.utils import getLogger
from rh.models import MovimentacaoTeletrabalho, Servidor
from datetime import datetime
import base64
from rh.pvf.models import ShiftManager
from rh.models import Lotacao, Servidor, ServidorLotacao
from django.db.models.query_utils import Q
from rh.pvf.models import PortalRequest


log = getLogger(__name__)


def get_data_report(params):
    data = []

    employees = Servidor.objects.filter(ativo=True).exclude(
        type_by_possession__in=[
            "SAP",
            "MAP",
            "MAP2",
            "APO",
            "BFP",
            "COE",
            "XXX",
            "TCR",
            "VOL",
            "JCA",
            "REX",
            "EXT",
            "CTR",
        ]
    )
    request = PortalRequest()
    for employee in employees:
        employee_capacity = ServidorLotacao.objects.filter(
            servidor=employee, designacao=False, ativo=True
        ).first()
        capacity = None
        if employee_capacity:
            capacity = employee_capacity.lotacao
        telework = MovimentacaoTeletrabalho.objects.filter(
            servidor=employee, ativo=True, data_fim__gte=datetime.now().date()
        ).first()

        data.append(
            {
                "Matricula": employee.matricula,
                "Nome": employee.pessoa_fisica.nome,
                "Chefe Imediato": (
                    employee.chefe_imediato.pessoa_fisica.nome
                    if employee.chefe_imediato
                    else ""
                ),
                "Lotação": capacity.nome if capacity else "",
                "Responsável": (
                    capacity.responsavel.pessoa_fisica.nome
                    if capacity and capacity.responsavel
                    else ""
                ),
                "Lotaçao Aprovador Portal": (
                    "SIM" if capacity and capacity.portal_approver else "NÃO"
                ),
                "Aprovador Vida Funcional": get_approver_vdf(request, employee),
                "Aprovador Teletrabalho": (
                    telework.aprovador.pessoa_fisica.nome if telework else "-"
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
        "keys": [
            "Matricula",
            "Nome",
            "Chefe Imediato",
            "Lotação",
            "Responsável",
            "Lotaçao Aprovador Portal",
            "Aprovador Vida Funcional",
            "Aprovador Teletrabalho",
        ],
    }
    return values


def get_approver_vdf(request, employee):
    try:
        return request.get_immediate_boss(employee).pessoa_fisica.nome
    except:
        pass
