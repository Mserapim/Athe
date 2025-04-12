from datetime import datetime
import decimal

from django.db.models import Q
from rh.gfp.models import FolhaEvento

from contrib.utils import getLogger
from standard.models import Choice

log = getLogger(__name__)


def validate_period_format(value):
    """
    Function to split a date by '/' and returns the month and year
    :params: value (str) string contains a date in MM/YYYY format

    :return: tuple
        [0] int - month
        [1] int - year
    """
    try:
        month, year = value.split("/")
        return month, year

    except Exception as error:
        log.error(error)
        raise AttributeError(
            " A Formatação das competências deve seguir o seguinte padrão: MM/AAAA (Ex.: 08/2023)"
        ) from error


def batch_queryset(queryset, batch_size=1000):
    """
    Function to split a queryset and organize by a batch_size amount
    :params: queryset (QuerySet) QuerySet to divide
    :params: batch_size (int) Max quantity of units for queryset return

    :returns: tuple
        [0] start (int) initial number of order of this division
        [1] end (int) end number of order of this division
        [2] total (int) total of elements in queryset
        [3] queryset (QuerySet) QuerySet of elements up to batch_size limit.
    """
    total = queryset.count()
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        yield (start, end, total, queryset[start:end])


def get_dict_choice_display(app, name, string_value=False):
    """
    Function to get all elements in a choice field and return a dict for the value (key)
    and the label
    :params: app (str) The 'app' field for Choice Model object
    :params: name (str) The 'name' field for Choice Model object
    :params: string_value (bool) True if the 'cvalue' field is the value of key in Choice Model

    :returns:  (dict)
    """
    format_dict = {}
    for key, value in Choice.get_choices_for(app, name, char_field=string_value):
        format_dict.update({key: value})
    return format_dict


def get_data_report(params: dict) -> dict:
    """
    Function responsible for generating report data, applies filters
    and organizes the data to be returned

    :returns: (dict)
    """

    data = []

    query = FolhaEvento.objects.filter()

    # Extract params
    end_competence = params["end_competence"]
    start_competence = params["start_competence"]
    active = params["active"]
    types_by_possession = params["types_by_possession"]
    type_report = params["type_report"]
    output_format = params["output_format"]

    # Apply filters
    query_filters = Q()
    if start_competence:
        month, year = validate_period_format(start_competence)
        query_filters &= Q(
            folha__periodo__mes__gte=int(month), folha__periodo__ano=int(year)
        )

    if end_competence:
        month, year = validate_period_format(end_competence)
        query_filters &= Q(
            folha__periodo__mes__lte=int(month), folha__periodo__ano=int(year)
        )

    if active and int(active) != 9999:
        if int(active):
            query_filters &= Q(servidor__ativo=True)
        else:
            query_filters &= Q(servidor__ativo=False)

    if types_by_possession:
        types_by_possession = types_by_possession.split(",")
        query_filters &= Q(servidor__type_by_possession__in=types_by_possession)

    if query_filters:
        query = query.filter(query_filters)

    if output_format == "CSV":
        if type_report == 1:
            query = query.select_related(
                "servidor", "evento", "servidor__pessoa_fisica"
            )
            events_by_server = {}
            format_category_employee = get_dict_choice_display(
                "rh", "CLASSIF_EMPLOYEE_BY_POSSESSION", True
            )
            format_mass_segregation_plan = get_dict_choice_display(
                "rh", "MASS_SEGREGATION_PLAN"
            )
            for _, __, ___, events in batch_queryset(query, batch_size=50000):
                for event in events:
                    server_id = event.servidor.id
                    month = str(event.folha.periodo.mes).zfill(2)
                    year = event.folha.periodo.ano
                    period = f"{month}/{year}"
                    if server_id not in events_by_server:
                        mass_segregation_plan = (
                            format_mass_segregation_plan.get(
                                event.servidor.socialsecurities.first().mass_segregation_plan,
                                None,
                            )
                            if event.servidor.socialsecurities.first()
                            else None
                        )
                        events_by_server[server_id] = {
                            "Matrícula": (
                                event.servidor.matricula if event.servidor else ""
                            ),
                            "Nome": (
                                event.servidor.pessoa_fisica.nome
                                if event.servidor
                                else ""
                            ),
                            "Data Nascimento": (
                                event.servidor.pessoa_fisica.data_nascimento
                                if event.servidor
                                else ""
                            ),
                            "Tipo Servidor": (
                                format_category_employee.get(
                                    event.servidor.type_by_possession, None
                                )
                                if event.servidor
                                else ""
                            ),
                            "Segregação de Massa": mass_segregation_plan,
                            "event": {},
                        }
                    if period not in events_by_server[server_id]["event"]:
                        events_by_server[server_id]["event"][period] = {
                            "Período": period
                        }

                    if (
                        f"{event.evento.titulo}"
                        not in events_by_server[server_id]["event"][period]
                    ):
                        events_by_server[server_id]["event"][period][
                            f"{event.evento.titulo}"
                        ] = (
                            event.valor
                            if decimal.Decimal(event.valor) > 0
                            else decimal.Decimal(0)
                        )
                    else:
                        events_by_server[server_id]["event"][period][
                            f"{event.evento.titulo}"
                        ] += (
                            event.valor
                            if decimal.Decimal(event.valor) > 0
                            else decimal.Decimal(0)
                        )

            for _, element in events_by_server.items():
                for __, _events in element.pop("event", {}).items():
                    data.append(
                        {
                            **element,
                            **_events,
                        }
                    )
            order_list = [
                "Período",
                "Matrícula",
                "Nome",
                "Data Nascimento",
                "Tipo Servidor",
                "Segregação de Massa",
            ]
        else:
            query = query.select_related(
                "servidor", "evento", "servidor__pessoa_fisica"
            )
            events_by_server = {}
            format_category_employee = get_dict_choice_display(
                "rh", "CLASSIF_EMPLOYEE_BY_POSSESSION", True
            )
            format_mass_segregation_plan = get_dict_choice_display(
                "rh", "MASS_SEGREGATION_PLAN"
            )
            for _, __, ___, events in batch_queryset(query, batch_size=50000):
                for event in events:
                    server_id = event.servidor.id
                    evento_id = event.evento.id
                    if server_id not in events_by_server:
                        mass_segregation_plan = (
                            format_mass_segregation_plan.get(
                                event.servidor.socialsecurities.first().mass_segregation_plan,
                                None,
                            )
                            if event.servidor.socialsecurities.first()
                            else None
                        )
                        events_by_server[server_id] = {
                            "Matrícula": (
                                event.servidor.matricula if event.servidor else ""
                            ),
                            "Nome": (
                                event.servidor.pessoa_fisica.nome
                                if event.servidor
                                else ""
                            ),
                            "Data Nascimento": (
                                event.servidor.pessoa_fisica.data_nascimento
                                if event.servidor
                                else ""
                            ),
                            "Tipo Servidor": (
                                format_category_employee.get(
                                    event.servidor.type_by_possession, None
                                )
                                if event.servidor
                                else ""
                            ),
                            "Segregação de Massa": mass_segregation_plan,
                            "event": {},
                        }
                    if evento_id not in events_by_server[server_id]["event"]:
                        events_by_server[server_id]["event"][evento_id] = {
                            "Título": event.evento.titulo,
                            "Número": event.evento.numero,
                        }
                    month = str(event.folha.periodo.mes).zfill(2)
                    year = event.folha.periodo.ano
                    period = f"{month}/{year}"
                    if (
                        f"{period}"
                        not in events_by_server[server_id]["event"][evento_id]
                    ):
                        events_by_server[server_id]["event"][evento_id][
                            f"{period}"
                        ] = event.valor
                    else:
                        events_by_server[server_id]["event"][evento_id][
                            f"{period}"
                        ] += event.valor

            for _, element in events_by_server.items():
                for __, _events in element.pop("event", {}).items():
                    data.append(
                        {
                            **element,
                            **_events,
                        }
                    )

            order_list = [
                "Matrícula",
                "Nome",
                "Data Nascimento",
                "Tipo Servidor",
                "Segregação de Massa",
                "Título",
                "Número",
            ]
    dates_list = sorted(set().union(*(d.keys() for d in data)).difference(order_list))

    values = {
        "title": params["report_name"],
        "data": data,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "keys": order_list + dates_list,
    }
    return values
