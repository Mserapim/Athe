from datetime import datetime, date, timedelta

from django.db.models import (
    Q,
    F,
    fields,
    Case,
    Value,
    When,
    CharField,
    ExpressionWrapper,
)
from contrib.utils import QuerySetChain

from rh.models import MovimentacaoTeletrabalho
from rh.pvf.const import (
    STS_EFFECTIVE,
    STS_WAI_SUBS_SCIENCE,
    STS_WAI_APPROVER,
    STS_WAI_EFFECTIVENESS,
    STS_REJECTED,
    STS_CORREGEDORIE_ADVISORY,
    STS_STAND_BY,
    STS_ESCALA_ENVIADA,
)

from contrib.utils import getLogger

log = getLogger(__name__)


# Função que busca os teletrabalhos por periodo mes/ano e filtro de todos/efetivados/pendentes
def get_query_teletrabalho_periodo(query=None, params=None):

    status_display_mapping = {
        STS_EFFECTIVE: "Efetivado",
        STS_WAI_SUBS_SCIENCE: "Aguardando Ciência do Substituto",
        STS_WAI_APPROVER: "Aguardando Aprovador",
        STS_WAI_EFFECTIVENESS: "Aguardando Efetivação",
        STS_REJECTED: "Indeferido",
        STS_CORREGEDORIE_ADVISORY: "Aguardando Assessoria da Corregedoria",
        STS_STAND_BY: "Aguardando Envio",
        STS_ESCALA_ENVIADA: "Escala Enviada",
        None: "Não Enviado",
    }
    campo_busca = [
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__icontains",
    ]

    periodo_ano = params.get("periodo_ano", None)
    periodo_mes = params.get("periodo_mes", None)
    filtro = params.get("filtro", None)
    busca = params.get("busca", None)

    inicio_periodo = date(periodo_ano, periodo_mes, 1)
    if periodo_mes == 12:
        fim_periodo = date(periodo_ano + 1, 1, 1) - timedelta(
            days=1
        )  # Próximo mês no primeiro dia, menos um
    else:
        fim_periodo = date(periodo_ano, periodo_mes + 1, 1) - timedelta(
            days=1
        )  # Próximo mês no primeiro dia, menos um

    if query is None:
        query = MovimentacaoTeletrabalho.objects.filter(
            Q(data_inicio__lt=fim_periodo, data_fim__gte=inicio_periodo)
        )

        if campo_busca and len(campo_busca) > 0:
            qf = None
            for index in campo_busca:
                q = Q(**{index: busca})
                qf = q if qf is None else Q(qf | q)

            query = query.filter(qf)

    query_efetivos = (
        query.filter(
            pvf_work_plan__reference_month=periodo_mes,
            pvf_work_plan__reference_year=periodo_ano,
            pvf_work_plan__status__in=[STS_EFFECTIVE],
        )
        .annotate(
            status=Case(
                *[
                    When(pvf_work_plan__status=value, then=Value(display))
                    for value, display in status_display_mapping.items()
                ],
                default=Value(
                    "Não Enviado"
                ),  # Valor padrão se não houver correspondência no mapeamento
                output_field=CharField()
            )
        )
        .annotate(
            solicitacao=ExpressionWrapper(
                F("pvf_work_plan__pk"), output_field=fields.IntegerField()
            )
        )
    )

    query_em_andamento = (
        query.filter(
            pvf_work_plan__reference_month=periodo_mes,
            pvf_work_plan__reference_year=periodo_ano,
            pvf_work_plan__status__in=[
                STS_WAI_SUBS_SCIENCE,
                STS_WAI_APPROVER,
                STS_WAI_EFFECTIVENESS,
                STS_CORREGEDORIE_ADVISORY,
                STS_STAND_BY,
                STS_ESCALA_ENVIADA,
            ],
        )
        .annotate(
            status=Case(
                *[
                    When(pvf_work_plan__status=value, then=Value(display))
                    for value, display in status_display_mapping.items()
                ],
                default=Value(
                    "Não Enviado"
                ),  # Valor padrão se não houver correspondência no mapeamento
                output_field=CharField()
            )
        )
        .annotate(
            solicitacao=ExpressionWrapper(
                F("pvf_work_plan__pk"), output_field=fields.IntegerField()
            )
        )
    )

    query_pendentes = (
        query.exclude(pk__in=query_efetivos)
        .exclude(pk__in=query_em_andamento)
        .annotate(status=Value("Não Enviado", output_field=CharField()))
        .annotate(solicitacao=Value("", output_field=CharField()))
    )

    if filtro == "todos":
        return QuerySetChain(query_efetivos, query_em_andamento, query_pendentes)

    if filtro == "efetivada":
        return query_efetivos

    if filtro == "pendente":
        return QuerySetChain(query_em_andamento, query_pendentes)
