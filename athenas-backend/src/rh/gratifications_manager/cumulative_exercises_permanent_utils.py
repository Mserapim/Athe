from decimal import Decimal

from django.db.models import Q, Count, Max

from contrib.utils import getLogger
from contrib.daterange import NewDateRange

from rh.models import ServidorLotacao, Servidor
from standard.models import Choice
from rh.models import ExercCumulPermanente, DesigsExercCumulPermanente

from rh.afastamento.afastamento_utils import buscar_afastamentos_periodo

log = getLogger(__name__)


def types_by_possession_membro():
    return ["MBR", "MEL", "MCM", "MEC", "MEL2", "MCM2", "MEC2"]


def buscar_desigs(dt_range):
    q = ServidorLotacao.objects.filter(
        servidor__type_by_possession__in=types_by_possession_membro(),
        designacao=True,
        from_substitution=False,
        data_vigencia_inicio__lte=dt_range.last,
    ).filter(
        Q(Q(data_vigencia_fim__isnull=True) | Q(data_vigencia_fim__gte=dt_range.first))
    )

    return q


def buscar_matriculas_desigs(q):
    return [
        x[0]
        for x in (
            q.values_list("servidor__matricula")
            .order_by("servidor")
            .annotate(count_servidor=Count("servidor"))
            .filter(count_servidor__gt=1)
        )
    ]


def buscar_desigs_servidor(matricula, q):
    return q.filter(
        servidor__matricula=matricula,
    )


def buscar_desigs_servidor_exerc_cumul(desigs_servidor):
    tag = Choice.objects.filter(name="WORKPLACE_TAG", description="00800").first().value
    return desigs_servidor.filter(
        Q(
            Q(lotacao__nome__icontains="PROMOTORIA ")
            | Q(lotacao__nome__icontains="PROCURADORIA ")
        )
        | Q(lotacao__workplace_config_tags__tag=tag)
    )


def buscar_pct_designacao(desigs, desig):
    q = desigs.filter(
        lotacao=desig.lotacao,
        cumulativa=True,
    ).exclude(main=True)

    qtd = (
        q.values("servidor")
        .annotate(total=Count("servidor"))
        .order_by("servidor")
        .count()
    )
    if qtd == 0:
        return None
    else:
        tag = (
            Choice.objects.filter(name="WORKPLACE_TAG", description="00800")
            .first()
            .value
        )
        if q.filter(
            lotacao__workplace_config_tags__tag=tag,
        ).exists():
            return Decimal(10)
        elif desig.data_vigencia_fim:
            return Decimal(10) if qtd == 1 else (Decimal(10) / Decimal(qtd))
        elif desig.data_vigencia_fim is None:
            return Decimal(15) if qtd == 1 else (Decimal(15) / Decimal(qtd))


def buscar_desig_base_calculo(designacoes):
    q = designacoes.exclude(pct__isnull=True, principal=True)

    cumulativas = q.filter(cumulativa=True)
    if cumulativas.count() == 1:
        return cumulativas.first()
    elif cumulativas.count() > 1:
        q = cumulativas.order_by("-pct")
        return q.first()
    else:
        q = q.order_by("-pct")
        return q.first()


def buscar_range_consolidado(desigs, dt_range_periodo):
    dt_inicio = None
    dt_fim = None
    for d in desigs:
        dt_inicio = (
            d.data_vigencia_inicio
            if dt_inicio is None or d.data_vigencia_inicio <= dt_inicio
            else dt_inicio
        )
        dt_fim = (
            d.data_vigencia_fim
            if (
                dt_fim is None
                or (
                    d.data_vigencia_fim is not None
                    and dt_fim is not None
                    and dt_fim >= d.data_vigencia_fim
                )
            )
            else dt_fim
        )

    if dt_range_periodo.first > dt_inicio:
        dt_inicio = dt_range_periodo.first

    if dt_fim is None or (dt_fim is not None and dt_range_periodo.last < dt_fim):
        dt_fim = dt_range_periodo.last

    return NewDateRange(dt_inicio, dt_fim)


def buscar_qtd_dias_cons_afast(desigs, dt_range_periodo):
    qtd_dias_consolidado = 0
    qtd_dias_afastamento = 0

    for desig in desigs.exclude(principal=True):
        dt_fim_desig = (
            dt_range_periodo.last
            if desig.data_vigencia_fim is None
            else desig.data_vigencia_fim
        )
        dt_range_desig = NewDateRange(desig.data_vigencia_inicio, dt_fim_desig)

        dt_range_intersect_desig = dt_range_desig.intersect(dt_range_periodo)
        qtd_dias_afast_desig = buscar_afastamentos_periodo(
            desig.exerc_cumul_perm.servidor, dt_range_intersect_desig
        )

        qtd_dias_consolidado += dt_range_intersect_desig.days
        qtd_dias_afastamento += qtd_dias_afast_desig

    if qtd_dias_consolidado > dt_range_periodo.days:
        qtd_dias_consolidado = dt_range_periodo.days

    if qtd_dias_afastamento > dt_range_periodo.days:
        qtd_dias_afastamento = dt_range_periodo.days

    return {
        "qtd_dias_consolidado": qtd_dias_consolidado,
        "qtd_dias_afastamento": qtd_dias_afastamento,
    }


def buscar_qtd_dias_consolidado(qtd_dias_periodo, qtd_dias_consolidado, qtd_dias_afast):
    qtd_dias = qtd_dias_consolidado - qtd_dias_afast

    if qtd_dias < 0:
        return 0
    elif qtd_dias > qtd_dias_periodo:
        return qtd_dias_periodo
    else:
        return qtd_dias


def calcular_exerc_cumul_permanente(
    periodo, matriculas_ignorar, matricula, desigs, dt_range_periodo
):
    criar_cumul_perm = False
    if matricula not in matriculas_ignorar:
        desigs_servidor = buscar_desigs_servidor(matricula, desigs)
        desigs_exerc_cumul = buscar_desigs_servidor_exerc_cumul(desigs_servidor)
        desigs_exerc_cumul_valido = desigs_exerc_cumul.exists()
        for desig in desigs_servidor:
            if desig.cumulativa and desigs_exerc_cumul_valido:
                criar_cumul_perm = True

        if criar_cumul_perm:
            exerc_cumul_perm = ExercCumulPermanente(
                servidor=Servidor.objects.get(matricula=matricula),
                periodo=periodo,
            )
            exerc_cumul_perm.save()

            for desig in desigs_servidor:
                if desig.cumulativa:
                    desig_exerc_cumul_perm = DesigsExercCumulPermanente(
                        exerc_cumul_perm=exerc_cumul_perm,
                        designacao=desig.lotacao,
                        substituicao=desig.from_substitution,
                        ativo=desig.ativo,
                        principal=desig.main,
                        responsavel=desig.responsible,
                        titular=desig.owner,
                        coordenador=desig.coordinator,
                        prejuizo=desig.prejudice,
                        acao=desig.action,
                        data_vigencia_inicio=desig.data_vigencia_inicio,
                        data_vigencia_fim=desig.data_vigencia_fim,
                        cumulativa=desig.cumulativa,
                    )

                    pct_desig = buscar_pct_designacao(desigs_servidor, desig)

                    if pct_desig is not None:
                        desig_exerc_cumul_perm.pct = pct_desig

                    desig_exerc_cumul_perm.save()

            desig_base_calculo = buscar_desig_base_calculo(
                exerc_cumul_perm.designacoes.all()
            )
            if desig_base_calculo is not None:
                desig_base_calculo.base_calculo = True
                desig_base_calculo.save()

                qtd_dias_cons_afast = buscar_qtd_dias_cons_afast(
                    exerc_cumul_perm.designacoes.all(), dt_range_periodo
                )
                qtd_dias_consolidado = qtd_dias_cons_afast["qtd_dias_consolidado"]
                qtd_dias_afast = qtd_dias_cons_afast["qtd_dias_afastamento"]

                exerc_cumul_perm.pct_consolidado = desig_base_calculo.pct
                exerc_cumul_perm.qtd_dias_afastamento = qtd_dias_afast
                exerc_cumul_perm.qtd_dias_consolidado = buscar_qtd_dias_consolidado(
                    dt_range_periodo.days, qtd_dias_consolidado, qtd_dias_afast
                )
                exerc_cumul_perm.save()
