import base64
from datetime import datetime
from django.db.models import Q

from contrib.utils import getLogger
from ceaf.models import Participant

log = getLogger(__name__)


def validate_period_format(value):

    try:
        month, year = value.split("/")
        return month, year
    except Exception as e:
        log.error(e)
        raise Exception(
            "A Formatação das competências deve seguir o seguinte padrão: MM/AAAA (Ex.: 08/2023)"
        )


def get_data_report(params):

    data = []

    query = Participant.objects.filter()

    # Extract params
    start_matricula = params["start_matricula"]
    end_matricula = params["end_matricula"]
    type_by_possession = params["type_by_possession"]
    capacitation = params["capacitation"]
    end_competence = params["end_competence"]
    start_competence = params["start_competence"]
    name = params["name"]
    output_format = params["output_format"]

    # ADD filters
    filter = []
    if start_matricula:
        filter.append(Q(employee__matricula__gte=int(start_matricula)))
    if end_matricula:
        filter.append(Q(employee__matricula__lte=int(end_matricula)))
    if type_by_possession:
        filter.append(Q(employee__type_by_possession__in=[type_by_possession]))
    if capacitation:
        filter.append(Q(capacitation__pk=int(capacitation)))
    if start_competence:
        month, year = validate_period_format(start_competence)
        filter.append(
            Q(
                Q(capacitation__month__gte=int(month), capacitation__year=int(year))
                | Q(capacitation__year__gt=int(year))
            )
            & Q(capacitation__year__isnull=False)
        )
    if end_competence:
        month, year = validate_period_format(end_competence)
        filter.append(
            Q(
                Q(capacitation__month__lte=int(month), capacitation__year=int(year))
                | Q(capacitation__year__lt=int(year))
            )
            & Q(capacitation__year__isnull=False)
        )

    if name:
        filter.append(Q(name__icontains=name))

    q_filter = None
    for qf in filter:
        if not q_filter:
            q_filter = qf
        else:
            q_filter = q_filter & qf
    if q_filter:
        query = query.filter(q_filter)

    # Generate data dict
    for q in query.order_by("name").distinct("name"):
        if output_format == "PDF":
            capacitations = []
            for participant in query.filter(name=q.name).order_by(
                "capacitation__year", "capacitation__month"
            ):
                capacitations.append(
                    {
                        "reference_period": participant.capacitation.reference_period,
                        "capacitation_name": participant.capacitation.name,
                        "local": participant.capacitation.local,
                        "time_total": str(participant.capacitation.time_total),
                        "period": participant.capacitation.period,
                        "type_participant": participant.get_type_participant_display(),
                    }
                )
            data.append(
                {
                    "name": q.employee.pessoa_fisica.nome if q.employee else q.name,
                    "matricula": q.employee.matricula if q.employee else "",
                    "type_by_possession": (
                        q.employee.get_type_by_possession_display()
                        if q.employee and q.employee.get_type_by_possession_display()
                        else ""
                    ),
                    "capacitations": capacitations,
                }
            )
        if output_format == "XLS":
            for participant in query.filter(name=q.name).order_by(
                "capacitation__year", "capacitation__month"
            ):
                data.append(
                    {
                        "name": q.employee.pessoa_fisica.nome if q.employee else q.name,
                        "matricula": q.employee.matricula if q.employee else "",
                        "type_by_possession": (
                            q.employee.get_type_by_possession_display()
                            if q.employee
                            and q.employee.get_type_by_possession_display()
                            else ""
                        ),
                        "reference_period": participant.capacitation.reference_period,
                        "capacitation_name": participant.capacitation.name,
                        "local": participant.capacitation.local,
                        "time_total": str(participant.capacitation.time_total),
                        "period": participant.capacitation.period,
                        "type_participant": participant.get_type_participant_display(),
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
            "Nome",
            "Matricula",
            "Categoria do Servidor",
            "Referência",
            "Capacitação",
            "Local",
            "Tempo Total",
            "Período",
            "Tipo Participante",
        ],
    }
    return values
