from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.db.models import Q, Case, When, CharField

from standard.models import Choice, Item
from rh.gfp.models import Servidor, Folha, Evento
from rh.models import ServidorLotacao, GratMembros, Gratificacao, WorkplaceConfigTag

from contrib.utils import getLogger
from contrib.middleware import get_current_user, set_current_user
from contrib.daterange import NewDateRange
from rh.gfp.paycheckdifference_utils import calc_from_period
from rh.gratifications_manager.gm_utils import buscar_registro_gcpp

log = getLogger(__name__)


def buscar_membros_ativos():
    types_by_possession = ["MBR", "MEL", "MCM", "MEC", "MBR2", "MEL2", "MCM2", "MEC2"]
    return Servidor.objects.filter(
        type_by_possession__in=types_by_possession, ativo=True
    )


def verificar_posse_servidor(servidor, dt_range_periodo):
    return (
        servidor.posses_ativas.filter(
            data_exercicio__lte=dt_range_periodo.last,
        )
        .filter(
            Q(data_desligamento__isnull=True)
            | Q(data_desligamento__gte=dt_range_periodo.first)
        )
        .exists()
    )


def buscar_designacoes(servidor, dt_range_periodo):
    """
    Método para buscar as designações de um Servidor.
    - Designações são registros da tabela ServidorLotação que tem o campo 'designacao' sendo 'True'.

    A regra padrão é:
    - Só deve retornar designações que não são de substituição e somente dentro do período de vigência do mês desejado.

    Exceção:
    - A verba 02700 (Exercício Cumulativo Substituição Coordenação) também deve entrar na query, porém sendo para
    designações de substituição e somente dentro do período do mês anterior ao de referência do cálculo.
    """

    tag = 30  # Valor do id da TAG para a verba 02700 - EXERCÍCIO CUMULATIVO SUBSTITUIÇÃO COORDENAÇÃO
    mes_anterior = datetime(
        dt_range_periodo.first.year, dt_range_periodo.first.month, 1
    ) - relativedelta(months=1)
    range_periodo_mes_anterior = NewDateRange.range_from_month(
        mes_anterior.year, mes_anterior.month
    )
    dt_range_periodo_mes_anterior = NewDateRange(
        range_periodo_mes_anterior[0], range_periodo_mes_anterior[1]
    )

    return (
        ServidorLotacao.objects.distinct("pk")
        .filter(
            servidor=servidor,
            designacao=True,
        )
        .filter(
            Q(
                Q(
                    from_substitution=False,
                    data_vigencia_inicio__lte=dt_range_periodo.last,
                )
                & Q(
                    Q(data_vigencia_fim__isnull=True)
                    | Q(data_vigencia_fim__gte=dt_range_periodo.first)
                )
            )
            | Q(
                Q(
                    from_substitution=True,
                    data_vigencia_inicio__lte=dt_range_periodo_mes_anterior.last,
                    lotacao__workplace_config_tags__tag=tag,
                )
                & Q(
                    Q(data_vigencia_fim__isnull=True)
                    | Q(data_vigencia_fim__gte=dt_range_periodo_mes_anterior.first)
                )
            )
        )
        .order_by("pk")
    )


def criar_grat_membro(servidor, designacoes, periodo, user=None):
    set_current_user(user)

    grat_membro, criado = GratMembros.objects.get_or_create(
        servidor=servidor,
        periodo=periodo,
    )
    grat_membro.data_ultimo_calculo = datetime.today()
    grat_membro.save()

    if criado is False and grat_membro.designacoes.exists():
        grat_membro.designacoes.clear()
    grat_membro.designacoes.add(*designacoes)

    return grat_membro


def buscar_lotacoes(designacoes, ignorar_lotacoes_ids=None):
    if ignorar_lotacoes_ids:
        return [
            desig.lotacao
            for desig in designacoes
            if desig.lotacao.pk not in ignorar_lotacoes_ids
        ]
    else:
        return [desig.lotacao for desig in designacoes]


def buscar_config_tags_lotacoes(
    lotacoes, lotacoes_anteriores, dt_range_periodo, tipo_servidor
):
    """
    Método responsável por buscar as tags de configurações das lotações.
    A tag é um código de uma verba, e esse código gera o vínculo entre a lotação e a verba.

    Exceção:
    - Quando o Servidor for um tipo Membro e a Lotação houver mais de uma tag de verbas concorrentes, deve
    retornar somente a tag com maior peso.
    - Nunca retornar a tag 32 (00800 - EXERCÍCIO CUMULATIVO PERMANENTE)
    """

    q_tags = q_workplace_config_tag(dt_range_periodo)

    if tipo_servidor != "M":
        q_tags = q_tags.filter(workplace__in=lotacoes)
        tags = [x.tag for x in q_tags]
    else:
        tags = []
        verbas_concorrentes = Item.objects.get(key="gratifications_check").value.split(
            ","
        )
        for lotacao in lotacoes:
            tags_lotacao = []
            q_tags_lotacao = q_tags.filter(workplace=lotacao)

            if lotacao in lotacoes_anteriores and q_tags_lotacao.filter(tag="30"):
                tags.append("30")
            else:
                verbas_concorrentes_comparar = []
                if q_tags_lotacao.count() == 1:
                    tags_lotacao = tags_lotacao + [
                        int(x.tag) for x in q_tags_lotacao if x.tag != "32"
                    ]
                elif q_tags_lotacao.count() > 1:
                    eventos_lotacao = [
                        buscar_evento_por_tag(x.tag)
                        for x in q_tags_lotacao
                        if x.tag != "32"
                    ]
                    for evento in eventos_lotacao:
                        if evento in verbas_concorrentes:
                            verbas_concorrentes_comparar.append(
                                buscar_tag_por_evento(evento)
                            )
                        else:
                            tags_lotacao.append(buscar_tag_por_evento(evento))

                if len(tags_lotacao) > 0 or len(verbas_concorrentes_comparar) > 0:
                    tags = tags + tags_lotacao
                    tags = add_verbas_concorrentes(tags, verbas_concorrentes_comparar)

    return tags


def add_verbas_concorrentes(tags, verbas_concorrentes_comparar):
    """
    Método responsável por inserir às tags as verbas que são de concorrência

    Se houver apenas uma, ela mesma será adicionada às tags.
    Se houver mais de uma, será feita uma comparação entre elas e adicionada às tags somente a de maior peso
    """

    if len(verbas_concorrentes_comparar) == 1:
        tags = tags + verbas_concorrentes_comparar
    elif len(verbas_concorrentes_comparar) > 1:
        evento_maior_peso = (
            q_choice()
            .filter(value__in=verbas_concorrentes_comparar)
            .order_by("-order_weight")
            .first()
        )
        tags.append(evento_maior_peso.value)

    return tags


def q_workplace_config_tag(dt_range_periodo):
    """
    Método responsável por retornar uma query do modelo WorkplaceConfigTag.
    Para facilitar o script.
    """

    return WorkplaceConfigTag.objects.exclude(
        Q(start_validity__gt=dt_range_periodo.last)
        | (~Q(end_validity=None) & Q(end_validity__lt=dt_range_periodo.first))
    )


def q_choice():
    """
    Método responsável por retornar uma query do modelo Choice.
    Para facilitar o script.
    """

    return Choice.objects.filter(app_label="rh", name="WORKPLACE_TAG")


def buscar_evento_por_tag(tag):
    """
    Método responsável por buscar os números dos eventos a partir das tags
    """

    try:
        return q_choice().filter(value=tag).first().description
    except:
        return None


def buscar_tag_por_evento(evento):
    """
    Método responsável por buscar as tags a partir dos números dos eventos
    """

    try:
        return q_choice().filter(description=evento).first().value
    except:
        return None


def buscar_eventos(tags):
    CUMULATIVAS = ["03000", "13600", "07600"]

    choices = q_choice().filter(value__in=tags).order_by("-order_weight")

    choices = ["%s" % t for t in choices.values_list("description", flat=True)]
    order_list = CUMULATIVAS + choices

    query = Evento.objects.filter(Q(numero__in=choices) | Q(numero="07600"))
    query = query.annotate(
        position=Case(
            *[When(**{"numero": val}, then=pos) for pos, val in enumerate(order_list)],
            output_field=CharField(),
        ),
    )
    query = query.order_by("position")

    gratificacoes = []
    for evento in query:
        if evento.numero in CUMULATIVAS:
            gratificacoes.append(
                {"evento": evento, "cumulativa": True, "principal": False}
            )
        else:
            tem_principal = [x["principal"] for x in gratificacoes if x["principal"]]
            principal = False if tem_principal else True
            gratificacoes.append(
                {"evento": evento, "cumulativa": False, "principal": principal}
            )

    return gratificacoes


def buscar_gratificacoes(designacoes, dt_range_periodo, tipo_servidor):
    designacoes_mes_vigente = buscar_designacoes_mes_vigentes(
        designacoes, dt_range_periodo
    )
    lotacoes = buscar_lotacoes(designacoes)
    lotacoes_anteriores = buscar_lotacoes(
        designacoes, [x.pk for x in buscar_lotacoes(designacoes_mes_vigente)]
    )
    tags = buscar_config_tags_lotacoes(
        lotacoes, lotacoes_anteriores, dt_range_periodo, tipo_servidor
    )

    return buscar_eventos(tags)


def buscar_designacoes_mes_vigentes(designacoes, dt_range_periodo):
    return designacoes.exclude(
        data_vigencia_fim__isnull=False, data_vigencia_fim__lt=dt_range_periodo.first
    )


def filtrar_gratificacoes(
    grat_membro, gratificacoes, designacoes, dt_range_periodo, user=None
):
    """
    Método responsável por filtrar as gratificações que deverão entrar no cálculo.

    A lógica só irá incluir para realizar o cálculo nos casos:
        - se não existir a gratificação
        - se já existe a gratificação, estiver com o status 'EM AVALIAÇÃO' e com o campo qtd_dias_deferido nulo (não pode estar zero)
        - para as verbas 11400 e 02700 há regras específicas:
            - a verba 02700 exige que o Servidor tenha alguma designação de Substituição.

    A lógica também verifica se existe vínculo da gratificação com a GCPP, se existir deve-se recalcular.
    """
    set_current_user(user)

    grats_filtradas = []
    for grat in gratificacoes:
        gcpp = None
        calcular_grat = False

        q_grat = Gratificacao.objects.filter(
            grat_membro=grat_membro,
            evento=grat["evento"],
        )

        if q_grat.filter(status="AVAL", qtd_dias_deferido=None):
            calcular_grat = True
            gratificacao = q_grat.first()
        elif q_grat.filter(status__in=["DEFER", "INDEFER"]).exists() is False:
            calcular_grat = True
            gratificacao = Gratificacao(
                grat_membro=grat_membro,
                evento=grat["evento"],
            )

        if calcular_grat:
            q_gcpp = buscar_registro_gcpp(
                grat_membro.servidor,
                grat["evento"],
                grat_membro.periodo.ano,
                grat_membro.periodo.mes,
            )
            if q_gcpp.exists() and q_gcpp.first().status in ["analise", "apto"]:
                gcpp = q_gcpp.first()

            designacoes_mes_vigente = buscar_designacoes_mes_vigentes(
                designacoes, dt_range_periodo
            )
            if grat["evento"].numero != "02700" or (
                grat["evento"].numero == "02700"
                and designacoes.filter(from_substitution=True).exists()
            ):
                grats_filtradas.append(
                    {
                        "gratificacao": gratificacao,
                        "registro_gcpp": gcpp,
                    }
                )

    return grats_filtradas


def gravar_gratificacoes(periodo, grat_membro, gratificacoes, user=None):
    if gratificacoes:
        set_current_user(user)

        folha = Folha.objects.get(
            tipo_folha__titulo="NORMAL",
            periodo__ano=periodo.ano,
            periodo__mes=periodo.mes,
        )

        for i, grat in enumerate(gratificacoes):
            res = calc_from_period(
                grat_membro.servidor, folha, grat["gratificacao"].evento
            )
            qtd_calculado = res["qnt"]

            grat["gratificacao"].qtd_dias_consolidado = qtd_calculado
            grat["gratificacao"].qtd_dias_deferido = None
            grat["gratificacao"].status = "AVAL"
            grat["gratificacao"].ordem = i + 1
            grat["gratificacao"].data_ultimo_calculo = datetime.today()

            grat["gratificacao"].save()

            if grat["registro_gcpp"] is not None:
                if qtd_calculado in [None, 0]:
                    grat["registro_gcpp"].delete()
                else:
                    grat["registro_gcpp"].qtd_dias_confirmado = qtd_calculado
                    grat["registro_gcpp"].qtd_dias_calculado = None
                    grat["registro_gcpp"].valor_calculado = None
                    grat["registro_gcpp"].qtd_dias_pgto = None
                    grat["registro_gcpp"].valor_pgto = None
                    grat["registro_gcpp"].status = "analise"
                    grat["registro_gcpp"].save()
