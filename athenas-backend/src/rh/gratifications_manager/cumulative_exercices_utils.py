from datetime import datetime

from django.db.models import Q

from contrib.utils import getLogger
from contrib.daterange import NewDateRange

from rh.models import (
    ConfigPeriodoCumulativoSubstituicao,
    MovimentacaoSubstituicao,
    MovesSubstitutionsConsolidated,
)

log = getLogger(__name__)


def validar_periodo_vigente_exerc_cumul_subs():
    periodo = None
    success = True
    msg = ""

    hoje = datetime.today().date()

    q_config_periodo = ConfigPeriodoCumulativoSubstituicao.objects.filter(
        Q(data_inicio_periodo__lte=hoje, data_fim_periodo__gte=hoje)
        | Q(data_inicio_periodo__gte=hoje)
    ).order_by("data_inicio_periodo__year", "data_inicio_periodo__month")

    if q_config_periodo.exists() is False:
        success = False
        msg = "Não há configuração de período futuro."
    else:
        periodo = q_config_periodo.first()

    return {
        "periodo": periodo,
        "success": success,
        "msg": msg,
    }


def consolidar_exerc_cumul_subs(employee, employee_movs_ids, periodo_cumul_subs_id):
    movs = MovimentacaoSubstituicao.objects.filter(pk__in=employee_movs_ids).order_by(
        "data_inicio"
    )

    info = None
    ranges = [
        (mov.financial_effect_date_start, mov.financial_effect_date_end) for mov in movs
    ]
    cons_ranges = NewDateRange.consolidate_ranges_of_date(ranges)
    days_consolidated = sum([(x[1] - x[0]).days + 1 for x in cons_ranges])

    q_movs_cons = MovimentacaoSubstituicao.objects.filter(
        substitutions_consolidated__employee=employee
    ).exclude(able_to_pay=False)
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
                info = f"""
                Dos {days_consolidated} dias consolidados, há {days_intersect} dias
                em concomitância com outros períodos consolidados ou pagos que foram ignorados.
                """
                days_consolidated -= days_intersect

    mov_consolidated = MovesSubstitutionsConsolidated(
        employee=employee,
        days_consolidated=days_consolidated,
        info=info,
    )
    mov_consolidated.save()
    mov_consolidated.substitutions.set(movs)

    movs.update(consolidated=True, periodo_cumul_subs_id=periodo_cumul_subs_id)
