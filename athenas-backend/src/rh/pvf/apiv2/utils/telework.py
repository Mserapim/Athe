import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django.db.models.query_utils import Q
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user

from rh.models import MovimentacaoTeletrabalho, Servidor
from rh.pvf.models import (
    PVFCancelamentoTeletrabalho,
    RelatorioSemestralTeletrabalho,
    SendingTelework,
)
from rh.teletrabalho.models import ConfigPeriodoEnvioRelatoriosSemestrais
from engine.mq.models import Task

from rh.pvf.const import *
from rh.pvf.tasks import send_mail_teletrabalho, envia_email_aprovador_teletrabalho

from contrib.utils import getLogger

log = getLogger(__name__)


def get_request_progress_telework():
    """
    Checa se já existe uma solicitação de teletrablaho em andamento
    :returns: (bool)
    """
    QTD_WORK_PLAN = 1
    count_progress = (
        SendingTelework.objects.filter(
            employee=employee_from_user(get_current_user()),
        )
        .exclude(
            status__in=[
                STS_REJECTED,
                STS_EFFECTIVE,
                STS_CANCELED_DGP,
                STS_CANCELED_APPLICANT,
            ]
        )
        .count()
    )

    count_work_plan = SendingTelework().get_count_workplan
    if count_work_plan == 0:  # trocar a quantidade para 1
        count_work_plan = QTD_WORK_PLAN
    if count_progress >= count_work_plan:
        return True
    return False


def solicitacao_cancelamento_andamento():
    """
    Checa se já existe uma solicitação de cancelamento de trabalho em andamenrto
    :returns: (bool)
    """

    total_progresso = (
        PVFCancelamentoTeletrabalho.objects.filter(
            employee=employee_from_user(get_current_user()),
        )
        .exclude(
            status__in=[
                STS_REJECTED,
                STS_EFFECTIVE,
                STS_CANCELED_DGP,
                STS_CANCELED_APPLICANT,
            ]
        )
        .count()
    )

    if total_progresso > 0:
        return True
    return False


def is_workplan(employee):
    """
    Função que verifica se o servidor tem plano de trabalho ativo
    Args:
        employee
    Returns:
        bool:
    """
    date_current = datetime.today().date()
    work_plan = MovimentacaoTeletrabalho.objects.filter(
        Q(servidor=employee),
        Q(data_fim__isnull=True)
        | Q(data_fim__isnull=False) & Q(data_fim__gte=date_current),
    )
    if work_plan:
        return True
    return False


def telework_pending(employee):
    """
    Função que verifica se o servidor tem plano de trabalho não enviado
    Args:
        employee
    Returns:
        bool:
    """
    mov_telework = MovimentacaoTeletrabalho.objects.filter(servidor=employee).last()
    if mov_telework:
        if mov_telework.data_fim:
            if (
                SendingTelework.objects.filter(
                    employee=employee,
                    reference_year=mov_telework.data_fim.year,
                    reference_month=mov_telework.data_fim.month,
                )
                .exclude(
                    status__in=[
                        STS_REJECTED,
                        STS_CANCELED_DGP,
                        STS_CANCELED_APPLICANT,
                        STS_STAND_BY,
                    ]
                )
                .exclude(cancelado_solicitacao=True)
                .count()
                > 0
            ):
                return False
            else:
                return True
        else:
            return True

    return False


def telework_pending_id(employee):
    """
    Função que verifica se o servidor tem plano de trabalho não enviado, retornando o id caso possua
    Args:
        employee
    Returns:
        int:
    """
    mov_telework = MovimentacaoTeletrabalho.objects.filter(servidor=employee).last()
    send_teleworks = SendingTelework.objects.filter(
        employee=employee,
        status__in=[
            STS_WAI_SUBS_SCIENCE,
            STS_WAI_APPROVER,
            STS_CORREGEDORIE_ADVISORY,
            STS_STAND_BY,
        ],
    ).last()
    if mov_telework and send_teleworks:
        if mov_telework.data_fim:
            if (
                SendingTelework.objects.filter(
                    employee=employee,
                    reference_year=mov_telework.data_fim.year,
                    reference_month=mov_telework.data_fim.month,
                )
                .exclude(
                    status__in=[
                        STS_REJECTED,
                        STS_CANCELED_DGP,
                        STS_CANCELED_APPLICANT,
                        STS_STAND_BY,
                    ]
                )
                .exclude(cancelado_solicitacao=True)
                .count()
                > 0
            ):
                return 0
            else:
                return send_teleworks.id
        else:
            return send_teleworks.id

    return 0


def tp_solicitacao_teletrabalho(employee):
    if employee.is_teletrabalho_bloqueado:
        return PORTAL_SOLICITACAO_DESBLOQUEIO_TELETRABALHO
    return PORTAL_TELEWORK_TYPE


def qtd_plano_trabalho():
    """
    Função que retorna quantos planos de trabalho a ser enviado
    Returns:
        int:
    """
    month, year = SendingTelework.get_reference_year_month()
    return SendingTelework.count_work_plan(month, year)


def gerar_intervalo_mensal(data_inicio, data_fim):
    """
    Função que retonar uma lista de referências conforme as datas informadas
    args:
        data_inicio (date): data incico do plano.
        data_fim (date): data fim do plano.
    returns:
        list: lista de referências conforme as datas informadas
    """
    ano_atual, mes_atual = data_inicio.year, data_inicio.month
    while date(ano_atual, mes_atual, 1) <= data_fim:
        yield date(ano_atual, mes_atual, 1)
        if mes_atual == 12:
            mes_atual = 1
            ano_atual += 1
        else:
            mes_atual += 1


def get_envios(obj):
    """
    Função que retorna de referências dos planos enviados
    args:
        obj (objeto): instancia do plano.
    returns:
        list: lista de referências dos planos enviados.
    """
    periodo = ConfigPeriodoEnvioRelatoriosSemestrais.objects.last()
    if not periodo:
        return []

    mes_inicio_analisado, ano_inicio_analisado = map(
        int, periodo.data_inicio_periodo_analisado.split("/")
    )
    mes_fim_analisado, ano_fim_analisado = map(
        int, periodo.data_fim_periodo_analisado.split("/")
    )
    data_inicio_analisado = date(ano_inicio_analisado, mes_inicio_analisado, 1)
    ultimo_dia_mes_fim_analisado = calendar.monthrange(
        ano_fim_analisado, mes_fim_analisado
    )[1]
    data_fim_analisado = date(
        ano_fim_analisado, mes_fim_analisado, ultimo_dia_mes_fim_analisado
    )

    inicio_plano = max(obj.data_inicio, data_inicio_analisado)
    fim_plano = min(obj.data_fim, data_fim_analisado)

    meses_envios = []
    for data in gerar_intervalo_mensal(inicio_plano, fim_plano):
        if data_inicio_analisado <= data <= data_fim_analisado:
            meses_envios.append(data.strftime("%m/%Y"))

    return meses_envios


def aprovador_semestral(servidor, data_atual):
    """
    Função que retorna se o servidor é aprovador do teletrabalho no período informado
    args:
        servidor (objeto): instancia do servidor.
        data_atual: (date)
    returns:
        bool: informar se é aprovador do teletrabalho no período informado
    """
    periodo = ConfigPeriodoEnvioRelatoriosSemestrais.objects.last()
    relatorio_enviado = RelatorioSemestralTeletrabalho.objects.filter(
        periodo_envio=periodo, employee=servidor
    ).exists()
    if periodo and not relatorio_enviado:
        data_inicio_envio = periodo.data_inicio_periodo_envio
        data_fim_envio = periodo.data_fim_periodo_envio

        if data_inicio_envio <= data_atual <= data_fim_envio:
            mes_inicio_analisado, ano_inicio_analisado = map(
                int, periodo.data_inicio_periodo_analisado.split("/")
            )
            mes_fim_analisado, ano_fim_analisado = map(
                int, periodo.data_fim_periodo_analisado.split("/")
            )
            data_inicio_analisado = date(ano_inicio_analisado, mes_inicio_analisado, 1)
            ultimo_dia_mes_fim_analisado = calendar.monthrange(
                ano_fim_analisado, mes_fim_analisado
            )[1]
            data_fim_analisado = date(
                ano_fim_analisado, mes_fim_analisado, ultimo_dia_mes_fim_analisado
            )

            is_aprovador_teletrabalho = MovimentacaoTeletrabalho.objects.filter(
                Q(aprovador=servidor)
                & (
                    Q(data_inicio__lte=data_fim_analisado)
                    & Q(data_fim__gte=data_inicio_analisado)
                )
            ).exists()
            return is_aprovador_teletrabalho
    return False


def referencias_pendentes(servidor):
    """
    Função que retorna uma lista de refeências (mês/ano) de teletrabalho não enviados
    args:
        servidor (objeto): instancia do servidor
    returns:
        list: lista das referências
    """
    data_atual = datetime.today().date()
    referencias = []

    if is_workplan(servidor):
        for mes in range(1, 7):
            data_referencia = data_atual - relativedelta(months=mes)
            tele = MovimentacaoTeletrabalho.objects.filter(
                servidor=servidor, data_inicio__lte=data_referencia, ativo=True
            )

            if tele.exists():
                query = (
                    SendingTelework.objects.filter(
                        employee=servidor,
                        reference_month=data_referencia.month,
                        reference_year=data_referencia.year,
                    )
                    .exclude(
                        status__in=[
                            STS_REJECTED,
                            STS_CANCELED_DGP,
                            STS_CANCELED_APPLICANT,
                            STS_STAND_BY,
                        ]
                    )
                    .exclude(cancelado_solicitacao=True)
                )
                if not query.exists():
                    referencias.append(
                        f"{data_referencia.month}/{data_referencia.year}"
                    )
        return referencias
    else:
        query = MovimentacaoTeletrabalho.objects.filter(
            servidor=servidor, data_fim__lt=data_atual
        )
        if query.exists():
            ultimo_tele = query.last()
            data_referencia = ultimo_tele.data_fim

            if data_referencia > date(2023, 2, 1):
                for mes in range(1, 7):
                    tele = MovimentacaoTeletrabalho.objects.filter(
                        servidor=servidor, data_inicio__lte=data_referencia, ativo=True
                    )

                    if tele.exists():
                        query = (
                            SendingTelework.objects.filter(
                                employee=servidor,
                                reference_month=data_referencia.month,
                                reference_year=data_referencia.year,
                            )
                            .exclude(
                                status__in=[
                                    STS_REJECTED,
                                    STS_CANCELED_DGP,
                                    STS_CANCELED_APPLICANT,
                                    STS_STAND_BY,
                                ]
                            )
                            .exclude(cancelado_solicitacao=True)
                        )
                        if not query.exists():
                            referencias.append(
                                f"{data_referencia.month}/{data_referencia.year}"
                            )
                        data_referencia = ultimo_tele.data_fim - relativedelta(
                            months=mes
                        )
                return referencias
    return referencias


def teletrabalhos_ativos():
    """
    Função que retorna os teletrabalhos ativos na data de hoje
    Args:
    Returns:
        queryset:
    """
    data_atual = datetime.today().date()
    query = (
        MovimentacaoTeletrabalho.objects.filter(
            Q(data_inicio__lte=data_atual)
            & Q(Q(data_fim__isnull=True) | Q(data_fim__gte=data_atual))
        )
        .order_by("servidor__pk")
        .distinct("servidor")
    )
    return query


def tele_ativos_aprovar(servidor):
    """
    Função que retorna os teletrabalhos ativos na data de hoje relacionado a um aprovador
    Args:
        servidor: aprovador do teletrabalho
    Returns:
        queryset:
    """
    data_atual = datetime.today().date()
    query = (
        MovimentacaoTeletrabalho.objects.filter(aprovador=servidor)
        .filter(
            Q(data_inicio__lte=data_atual)
            & Q(Q(data_fim__isnull=True) | Q(data_fim__gte=data_atual))
        )
        .order_by("servidor__pk")
        .distinct("servidor")
    )
    return query


def teletrabalhos_finalizados_mes_anterior():
    """
    Função que retorna os teletrabalhos que foram finalizados no mês anterior
    Args:
    Returns:
        queryset:
    """
    data_atual = datetime.today().date()
    data_referencia = data_atual - relativedelta(months=1)
    data_inicio = data_referencia + relativedelta(day=1)
    query = (
        MovimentacaoTeletrabalho.objects.filter(
            Q(data_fim__gte=data_inicio) & Q(data_fim__lte=data_atual)
        )
        .order_by("servidor__pk")
        .distinct("servidor")
    )
    return query


def tele_finalizados_mes_anterior_aprovar(servidor):
    """
    Função que retorna os teletrabalhos que foram finalizados no mês anterior relacionado a um aprovador
    Args:
        servidor: aprovador do teletrabalho
    Returns:
        queryset:
    """
    data_atual = datetime.today().date()
    data_referencia = data_atual - relativedelta(months=1)
    data_inicio = data_referencia + relativedelta(day=1)
    query = (
        MovimentacaoTeletrabalho.objects.filter(aprovador=servidor)
        .filter(Q(data_fim__gte=data_inicio) & Q(data_fim__lte=data_atual))
        .order_by("servidor__pk")
        .distinct("servidor")
    )
    return query


def notifica_abertura_tele():
    """
    Função que será acionada do dia 1 ao dia 9 para notificar os servidores sobre a abertura do prazo de envio do teletrabalho
    """
    nm_template = "NOTIFICA_TELETRABALHO_TEMPLATE_1"
    servidores_a_notificar(nm_template)


def notifica_encerramento_tele():
    """
    Função que será acionada no dia 10 para notificar os servidores sobre o encerramento do prazo de envio do teletrabalho
    """
    nm_template = "NOTIFICA_TELETRABALHO_TEMPLATE_2"
    servidores_a_notificar(nm_template)


def notifica_nao_envio_tele():
    """
    Função que será acionada no dia 11 para notificar os servidores sobre o não envio do teletrabalho
    """
    nm_template = "NOTIFICA_TELETRABALHO_TEMPLATE_3"
    servidores_a_notificar(nm_template)


def servidores_a_notificar(nm_template):
    """
    Função que busca os teletrabalhos finalizados no mês anterior e os ativos, para serem notificados
    """
    data_referencia = datetime.today().date() - relativedelta(months=1)
    dt_fim_ref = data_referencia + relativedelta(day=31)
    teles = teletrabalhos_finalizados_mes_anterior().union(
        teletrabalhos_ativos(), all=False
    )
    teles_pk = list(teles.values_list("pk", flat=True))

    for tele_pk in teles_pk:
        tele = MovimentacaoTeletrabalho.objects.get(pk=tele_pk)
        if tele.data_inicio <= dt_fim_ref:
            query_request = (
                SendingTelework.objects.filter(
                    work_plan__pk=tele_pk,
                    reference_month=data_referencia.month,
                    reference_year=data_referencia.year,
                )
                .exclude(
                    status__in=[
                        STS_REJECTED,
                        STS_CANCELED_DGP,
                        STS_CANCELED_APPLICANT,
                        STS_STAND_BY,
                    ]
                )
                .exclude(cancelado_solicitacao=True)
            )

            if not query_request.exists():
                Task.start(
                    send_mail_teletrabalho,
                    description=f"Notificação teletrabalho",
                    tele_pk=tele_pk,
                    nm_template=nm_template,
                    user=get_current_user().id,
                )


def aprovadores_a_notificar():
    """
    Função que busca os teletrabalhos finalizados no mês anterior e os ativos, para serem notificados aos aprovadores
    """
    teles = teletrabalhos_finalizados_mes_anterior().union(
        teletrabalhos_ativos(), all=False
    )
    nm_template = "NOTIFICA_APROVADORES_PRAZO_TELETRABALHO"
    aprovadores = teles.distinct("aprovador").values_list("aprovador", flat=True)
    data_atual = datetime.today().date()
    data_referencia = data_atual - relativedelta(months=1)
    dt_fim_ref = data_referencia + relativedelta(day=31)

    for aprovador_id in aprovadores:
        aprovador = Servidor.objects.get(pk=aprovador_id)
        teles_aprovar = tele_finalizados_mes_anterior_aprovar(aprovador).union(
            tele_ativos_aprovar(aprovador), all=False
        )
        teles_pk = list(teles_aprovar.values_list("pk", flat=True))
        teles_pk_notificar = []

        for tele_pk in teles_pk:
            tele = MovimentacaoTeletrabalho.objects.get(pk=tele_pk)
            if tele.data_inicio <= dt_fim_ref:
                query_request = (
                    SendingTelework.objects.filter(
                        work_plan__pk=tele_pk,
                        reference_month=data_referencia.month,
                        reference_year=data_referencia.year,
                    )
                    .exclude(
                        status__in=[
                            STS_REJECTED,
                            STS_CANCELED_DGP,
                            STS_CANCELED_APPLICANT,
                            STS_STAND_BY,
                        ]
                    )
                    .exclude(cancelado_solicitacao=True)
                )

                if not query_request.exists():
                    teles_pk_notificar.append(tele_pk)

        if len(teles_pk_notificar) > 0:
            Task.start(
                envia_email_aprovador_teletrabalho,
                description=f"Notifica aprovadores teletrabalho",
                teles_pk=teles_pk_notificar,
                aprovador_pk=aprovador.pk,
                nm_template=nm_template,
                user=get_current_user().id,
            )
