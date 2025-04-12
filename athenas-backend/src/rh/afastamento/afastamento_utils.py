import calendar
from django.db.models import Q

from contrib.daterange import NewDateRange

from rh.afastamento.models import AfastamentoOutroOrgao, BaseLicencaAfastamento

from rh.const import CANCELADO as AFASTAMENTO_CANCELADO, TYPE_HEALTHHOURS
from rh.registerpoint.utils.ponto import inicio_fim_competencia


def buscar_afastamentos_periodo(servidor, dt_range):
    range_afastamento = NewDateRange()

    for mc in AfastamentoOutroOrgao.objects.filter(servidor=servidor).exclude(
        Q(data_inicio__gt=dt_range.last)
        | Q(onus=1)
        | Q(transito_pela_folha=True)
        | Q(estado=AFASTAMENTO_CANCELADO)
    ):
        range_afastamento += NewDateRange(mc.data_inicio, mc.data_fim)
    for absence in (
        BaseLicencaAfastamento.objects.filter(servidor=servidor)
        .exclude(Q(data_fim__lt=dt_range.first) | Q(data_inicio__gt=dt_range.last))
        .exclude(estado=AFASTAMENTO_CANCELADO)
    ):
        range_afastamento += NewDateRange(absence.data_inicio, absence.data_fim)

    if range_afastamento.days == 0:
        return 0
    else:
        range_inter = NewDateRange.range_intersect(
            [dt_range.first, dt_range.last],
            [range_afastamento.first, range_afastamento.last],
        )

        return NewDateRange(range_inter[0], range_inter[1]).days


def dias_afastamento_mes(servidor, mes, ano, meta):
    from rh.teletrabalho.utils import dias_afastamento_sem_recesso

    dt_inicio, dt_fim = inicio_fim_competencia(mes, ano)

    dt_inicio = meta.data_inicio if meta.data_inicio > dt_inicio else dt_inicio
    dt_fim = meta.data_fim if meta.data_fim < dt_fim else dt_fim

    qtd_dias_afastado = 0
    dias_diff_afastamento_recesso = 0
    afastamentos = (
        BaseLicencaAfastamento.objects.filter(
            Q(data_inicio__lte=dt_fim) & Q(data_fim__gte=dt_inicio),
            Q(servidor=servidor),
        )
        .exclude(estado=AFASTAMENTO_CANCELADO)
        .exclude(tipo=TYPE_HEALTHHOURS)
    )

    for afastamento in afastamentos:
        dt_fim_calc = dt_fim if dt_fim < afastamento.data_fim else afastamento.data_fim
        dt_inicio_calc = (
            dt_inicio
            if dt_inicio > afastamento.data_inicio
            else afastamento.data_inicio
        )
        dias_afastamento = NewDateRange(dt_inicio_calc, dt_fim_calc).days
        if mes == 1 or mes == 12:
            dias_sem_recesso = dias_afastamento_sem_recesso(
                ano, mes, dt_inicio_calc, dt_fim_calc
            )
            dias_diff_afastamento_recesso = (
                dias_diff_afastamento_recesso + dias_sem_recesso
            )

        qtd_dias_afastado = qtd_dias_afastado + dias_afastamento
    return qtd_dias_afastado, dias_diff_afastamento_recesso
