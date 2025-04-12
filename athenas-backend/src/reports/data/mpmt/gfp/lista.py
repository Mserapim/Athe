from datetime import datetime
import itertools

from django.db.models import Q, Count
from rh.gfp.models import FolhaEvento

from contrib.utils import getLogger

log = getLogger(__name__)


def validate_period_format(value):
    try:
        month, year = value.split("/")
        return month, year

    except Exception as e:
        log.error(e)
        raise Exception(
            " A Formatação das competências deve seguir o seguinte padrão: MM/AAAA (Ex.: 08/2023)"
        )


def batch_queryset(qs, batch_size=1000):
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
    total = qs.aggregate(count=Count("*"))["count"]
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        yield (start, end, total, qs[start:end])


def get_data_report(params: dict) -> dict:
    """
    Function: Função responsável pela geração de dados do relatório,
    aplica-se os filtros e organiza os dados a serem retornados
    :returns: (dict)
    """

    data = []

    query = FolhaEvento.objects.filter(status="CT")

    # Extract params
    end_competence = params["end_competence"]
    start_competence = params["start_competence"]
    active = params["active"]
    output_format = params["output_format"]
    types_by_possession = params["types_by_possession"]

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

    if output_format == "PDF":
        pass

    if output_format == "XLS":
        pass

    if output_format == "CSV":
        query = query.select_related(
            "servidor", "evento", "servidor__pessoa_fisica", "servidor__social_security"
        )
        for start, end, _, queryset in batch_queryset(query, batch_size=50000):
            batch = (
                {
                    "Segregação de Massa": (
                        q.servidor.social_security.get_mass_segregation_plan_display()
                        if q.servidor.social_security
                        else None
                    ),
                    "Mês": q.folha.periodo.mes,
                    "Ano": q.folha.periodo.ano,
                    "Período": f"{q.folha.periodo.mes} - {q.folha.periodo.ano}",
                    "Matrícula": q.servidor.matricula if q.servidor else "",
                    "Nome": q.servidor.pessoa_fisica.nome if q.servidor else "",
                    "Data Nascimento": (
                        q.servidor.pessoa_fisica.data_nascimento.strftime("%d/%m/%Y")
                        if q.servidor
                        else ""
                    ),
                    "Mês Nascimento": (
                        q.servidor.pessoa_fisica.data_nascimento.month
                        if q.servidor
                        else ""
                    ),
                    "Data Ini. Exercício": (
                        q.servidor.exercise_date if q.servidor else ""
                    ),
                    "Tipo Servidor": (
                        q.servidor.get_type_by_possession_display()
                        if q.servidor
                        else ""
                    ),
                    "Número": q.evento.numero,
                    "Título": q.evento.titulo,
                    "Valor": q.correct_valor,
                }
                for q in itertools.islice(queryset, end - start)
            )
            data.extend(batch)
    order_list = [
        "Segregação de Massa",
        "Mês",
        "Ano",
        "Período",
        "Matrícula",
        "Nome",
        "Data Nascimento",
        "Mês Nascimento",
        "Data Ini. Exercício",
        "Tipo Servidor",
        "Número",
        "Título",
        "Valor",
    ]

    values = {
        "title": params["report_name"],
        "data": data,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "keys": order_list,
    }
    return values
