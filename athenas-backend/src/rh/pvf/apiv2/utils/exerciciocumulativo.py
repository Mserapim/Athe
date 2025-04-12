from contrib.daterange import NewDateRange
from rh.models import MovimentacaoSubstituicao
from django.db.models import Q


def calc_dias_consolidados(solicitacao):
    """
    calcula quantos dias serão consolidados na solicitação de execicio cumulativo.
    Args:
        employee: servidor
        pk: id da solicitação
    Returns:
        int: qtd dias consolidados

    """
    movs = solicitacao.substituicoes.filter(indeferido=False)
    ranges = [
        (mov.financial_effect_date_start, mov.financial_effect_date_end) for mov in movs
    ]
    cons_ranges = NewDateRange.consolidate_ranges_of_date(ranges)
    dias_consolidados = sum([(x[1] - x[0]).days + 1 for x in cons_ranges])

    q_movs_cons = (
        MovimentacaoSubstituicao.objects.filter(
            substitutions_consolidated__employee=solicitacao.employee
        )
        .exclude(able_to_pay=False)
        .exclude(pk__in=movs.values_list("pk", flat=True))
    )
    if q_movs_cons.exists():
        cons_ranges_cons = []
        for mov in cons_ranges:
            q = q_movs_cons.filter(
                Q(financial_effect_date_start__gte=mov[0])
                | Q(financial_effect_date_end__gte=mov[1])
            )
            if q.exists():
                [cons_ranges_cons.append(m) for m in q]

        if cons_ranges_cons:
            ranges_cons = [
                (mov.financial_effect_date_start, mov.financial_effect_date_end)
                for mov in cons_ranges_cons
            ]
            cons_ranges_cons = NewDateRange.consolidate_ranges_of_date(ranges_cons)

            ranges_intersect = []
            for cons_range in cons_ranges:
                for cons_range_cons in cons_ranges_cons:
                    range_intersect = NewDateRange.range_intersect(
                        cons_range, cons_range_cons
                    )
                    if range_intersect:
                        ranges_intersect.append(range_intersect)

            if ranges_intersect:
                days_intersect = sum([(x[1] - x[0]).days + 1 for x in ranges_intersect])
                dias_consolidados -= days_intersect
    return dias_consolidados
