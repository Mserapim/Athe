import base64
from datetime import datetime
from django.db.models import Q
from rh.gfp.models import FolhaEvento

from contrib.utils import getLogger

log = getLogger(__name__)


def get_data_report(params: dict) -> dict:
    """
    Função responsável pela geração de dados do relatório,
    aplica-se os filtros e organiza os dados a serem retornados
    :returns: (dict)
    """

    data = []

    # Extract params
    payroll = int(params["payroll"])
    previous_payroll = int(params["previous_payroll"])
    type_by_possession = eval(params["type_by_possession"])
    unify = params["unify"]
    output_format = params["output_format"]

    # get query
    query = FolhaEvento.objects.filter(
        folha__pk__in=[payroll, previous_payroll]
    ).select_related("servidor", "evento")

    # Apply filters
    query_filters = Q()
    if type_by_possession:
        query_filters &= Q(servidor__type_by_possession__in=type_by_possession)

    if query_filters:
        query = query.filter(query_filters)

    if output_format == "PDF":
        # Group events by server
        servers = {}
        for event in query.order_by("-evento__tipo"):
            if event.servidor.id not in servers:
                servers[event.servidor.id] = {
                    "events": [],
                    "matricula": event.servidor.matricula,
                    "name": (
                        event.servidor.pessoa_fisica.nome
                        if event.servidor.pessoa_fisica
                        else ""
                    ),
                    "exercise_date": (
                        event.servidor.exercise_date.strftime("%d/%m/%Y")
                        if event.servidor.exercise_date
                        else ""
                    ),
                    "type_by_possession": event.servidor.get_type_by_possession_display(),
                }
            servers[event.servidor.id]["events"].append(event)

        # Compare events for each server
        for _, server in servers.items():
            events = server["events"]
            # events_dict = {f'{event.evento.numero}{event.info}': event for event in events if event.folha.pk == payroll}
            # previous_events_dict = {f'{event.evento.numero}{event.info}': event for event in events if event.folha.pk == previous_payroll}
            events_dict = get_events_dict(events, payroll, unify)
            previous_events_dict = get_events_dict(events, previous_payroll, unify)
            intersection = set(events_dict.keys()).intersection(
                previous_events_dict.keys()
            )
            difference = set(events_dict.keys()).symmetric_difference(
                previous_events_dict.keys()
            )
            events_list = []
            for item in intersection:
                event = events_dict[item]
                previous_event = previous_events_dict[item]
                event_correct_valor = set_correct_valor(event, unify)
                prev_event_correct_valor = set_correct_valor(previous_event, unify)
                events_list.append(
                    {
                        "event_code": event.evento.numero,
                        "event_description": set_event_description(
                            event=event, previous_event=previous_event, unify=unify
                        ),
                        "event_type": event.evento.tipo,
                        "actual_valor": event_correct_valor,
                        "last_valor": prev_event_correct_valor,
                        "status": (
                            "Mesmo valor"
                            if event_correct_valor == prev_event_correct_valor
                            else (
                                "Aumentou"
                                if event_correct_valor > prev_event_correct_valor
                                else "Diminuiu"
                            )
                        ),
                        "diff": (
                            f"{((float(event_correct_valor) / float(prev_event_correct_valor)) * 100.0):.2f} %"
                            if prev_event_correct_valor
                            else "-"
                        ),
                    }
                )
            for item in difference:
                if item in events_dict:
                    event = events_dict[item]
                    event_correct_valor = set_correct_valor(event, unify)
                    events_list.append(
                        {
                            "event_code": event.evento.numero,
                            "event_description": set_event_description(
                                event=event, previous_event=None, unify=unify
                            ),
                            "event_type": event.evento.tipo,
                            "actual_valor": event_correct_valor,
                            "last_valor": "",
                            "status": "Novo",
                            "diff": "",
                        }
                    )
                if item in previous_events_dict:
                    event = previous_events_dict[item]
                    prev_event_correct_valor = set_correct_valor(event, unify)
                    events_list.append(
                        {
                            "event_code": event.evento.numero,
                            "event_description": set_event_description(
                                event=event, previous_event=None, unify=unify
                            ),
                            "event_type": event.evento.tipo,
                            "actual_valor": "",
                            "last_valor": prev_event_correct_valor,
                            "status": "Sumiu",
                            "diff": "",
                        }
                    )

            server["events"] = sorted(
                events_list, key=lambda x: x["event_type"], reverse=True
            )
            data.append(server)

    if output_format == "XLS":
        # Group events by server
        servers = {}
        for event in query:
            if event.servidor.id not in servers:
                servers[event.servidor.id] = {
                    "events": [],
                    "Matrícula": event.servidor.matricula,
                    "Nome": (
                        event.servidor.pessoa_fisica.nome
                        if event.servidor.pessoa_fisica
                        else ""
                    ),
                    "Data Ini. Exercício": (
                        event.servidor.exercise_date.strftime("%d/%m/%Y")
                        if event.servidor.exercise_date
                        else ""
                    ),
                    "Tipo Servidor": event.servidor.get_type_by_possession_display(),
                }
            servers[event.servidor.id]["events"].append(event)

        # Compare events for each server
        for _, server in servers.items():
            events = server.pop("events")
            # events_dict = {f'{event.evento.numero}{event.info}': event for event in events if event.folha.pk == payroll}
            # previous_events_dict = {f'{event.evento.numero}{event.info}': event for event in events if event.folha.pk == previous_payroll}
            events_dict = get_events_dict(events, payroll, unify)
            previous_events_dict = get_events_dict(events, previous_payroll, unify)
            intersection = set(events_dict.keys()).intersection(
                previous_events_dict.keys()
            )
            difference = set(events_dict.keys()).symmetric_difference(
                previous_events_dict.keys()
            )
            events_list = []
            for item in intersection:
                event = events_dict[item]
                previous_event = previous_events_dict[item]
                event_correct_valor = set_correct_valor(event, unify)
                prev_event_correct_valor = set_correct_valor(previous_event, unify)
                server_data = {
                    **server,
                    **{
                        "Número": event.evento.numero,
                        "Título": set_event_description(
                            event=event, previous_event=previous_event, unify=unify
                        ),
                        "Tipo": event.evento.tipo,
                        "Valor Anterior": prev_event_correct_valor,
                        "Valor Atual": event_correct_valor,
                        "Status": (
                            "Mesmo valor"
                            if event_correct_valor == prev_event_correct_valor
                            else (
                                "Aumentou"
                                if event_correct_valor > prev_event_correct_valor
                                else "Diminuiu"
                            )
                        ),
                        "Diferença": (
                            f"{((float(event_correct_valor) / float(prev_event_correct_valor)) * 100.0):.2f} %"
                            if prev_event_correct_valor
                            else "-"
                        ),
                    },
                }

                data.append(server_data)
            for item in difference:
                server_data = server
                if item in events_dict:
                    event = events_dict[item]
                    event_correct_valor = set_correct_valor(event, unify)
                    server_data = {
                        **server,
                        **{
                            "Número": event.evento.numero,
                            "Título": set_event_description(
                                event=event, previous_event=None, unify=unify
                            ),
                            "Tipo": event.evento.tipo,
                            "Valor Anterior": None,
                            "Valor Atual": event_correct_valor,
                            "Status": "Novo",
                            "Diferença": None,
                        },
                    }
                if item in previous_events_dict:
                    event = previous_events_dict[item]
                    prev_event_correct_valor = set_correct_valor(event, unify)
                    server_data = {
                        **server,
                        **{
                            "Número": event.evento.numero,
                            "Título": set_event_description(
                                event=event, previous_event=None, unify=unify
                            ),
                            "Tipo": event.evento.tipo,
                            "Valor Anterior": prev_event_correct_valor,
                            "Valor Atual": None,
                            "Status": "Sumiu",
                            "Diferença": None,
                        },
                    }
                data.append(server_data)

    if output_format == "CSV":
        pass

    order_list = [
        "Matrícula",
        "Nome",
        "Data Ini. Exercício",
        "Tipo Servidor",
        "Número",
        "Título",
        "Tipo",
        "Valor Anterior",
        "Valor Atual",
        "Status",
        "Diferença",
    ]
    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    values = {
        "title": params["report_name"],
        "data": data,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
        "keys": order_list,
    }
    return values


def get_events_dict(events, payroll, unify):
    """
    Função responsável gerar o dict de eventos conforme o parâmetro de unifiy
    :returns: (dict)
    """
    if unify:
        values = {}
        for event in events:
            if event.folha.pk == payroll:
                if values.get(event.evento.numero):
                    values[event.evento.numero].sum_correct_valor = (
                        event.correct_valor
                        + values[event.evento.numero].sum_correct_valor
                    )
                    values[event.evento.numero].event_description = (
                        f"{values[event.evento.numero].event_description} {event.info}"
                    )
                else:
                    values.update({event.evento.numero: event})
                    values[event.evento.numero].sum_correct_valor = event.correct_valor
                    values[event.evento.numero].event_description = (
                        f"{event.evento.titulo}{event.info}"
                    )
        return values
    else:
        return {
            f"{event.evento.numero}{event.info}": event
            for event in events
            if event.folha.pk == payroll
        }


def set_correct_valor(event, unify):
    """
    Função responsável retorna o correct_valor conforme o parâmetro de unifiy
    :returns: (decimal)
    """
    return event.sum_correct_valor if unify else event.correct_valor


def set_event_description(event=None, previous_event=None, unify=None):
    """
    Função responsável retorna a descrição do evento conforme o parâmetro de unifiy
    :returns: (str)
    """
    if unify:
        if (
            previous_event
            and event.evento.numero == previous_event.evento.numero
            and f"{event.evento.titulo}{event.info}"
            != f"{previous_event.evento.titulo}{previous_event.info}"
        ):
            return f"{event.event_description} {previous_event.info}"

        return f"{event.event_description}"

    return f"{event.evento.titulo}{event.info}"
