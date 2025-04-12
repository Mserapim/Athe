from rh.afastamento.afastamento_utils import dias_afastamento_mes
from rh.const import (
    STATUS_TELETRABALHO_BLOQUEADO,
    STATUS_TELETRABALHO_DESBLOQUEADO,
    STATUS_TELETRABALHO_IGNORADO,
    STATUS_TELETRABALHO_PENDENTE,
    STATUS_TELETRABALHO_REGULAR,
    STATUS_TELETRABALHO_REVOGADO,
    STATUS_TELETRABALHO_CONCLUIDO,
    TYPE_HEALTHHOURS,
)
from rh.models import HistoricoMovTeletrabalho, MovimentacaoTeletrabalho
from rh.afastamento.models import BaseLicencaAfastamento
from rh.const import CANCELED
from rh.pvf.const import (
    MSG_DEFAULT_ATO_TELETRABALHO,
    STS_EFFECTIVE,
    STS_REJECTED,
    STS_STAND_BY,
    STS_CANCELED_APPLICANT,
    STS_CANCELED_DGP,
)
from rh.pvf.models import MarkTelework, SendingTelework
from rh.pvf.utils.folha_ponto import data_inicio_fim_referencia, proxima_referencia
from datetime import datetime
from django.db import models, transaction
from logging import getLogger
from ged.models import Arquivo
from rh.teletrabalho.notificacoes import (
    enviar_notificacao_email_servidor,
    enviar_notificacao_saldo_devedor,
)
import calendar
from contrib.daterange import NewDateRange


log = getLogger(__name__)

QTD_DIAS_RECESSO = 18

QTD_DIAS_BLOQUEIO = 10


def bloquear_mov_teletrabalho(
    mov_teletrabalho, observacao=None, anexo_id=None, status=None
):
    """
    Rotina que realiza o bloqueio do teletrabalho a partir do dia 11 do mês subsequente
    Obs: Não considerar afastamentos e retornos da solicitação após a data de corte
    no caso de afastamentos somar dias sem contar com os afastamento. após somar 10 dias bloquear.
    Args:
        mov_teletrabalho (obj): mov_teletrabalho.
        observacao (str).
        anexo_id (int).
        status (int). Status da solicitação do VDF
    """
    try:
        with transaction.atomic():
            qtd_bloqueios = (
                mov_teletrabalho.qtd_bloqueios + 1
                if mov_teletrabalho.qtd_bloqueios
                else 1
            )
            MovimentacaoTeletrabalho.objects.filter(pk=mov_teletrabalho.pk).update(
                situacao=STATUS_TELETRABALHO_BLOQUEADO, qtd_bloqueios=qtd_bloqueios
            )
            historico = HistoricoMovTeletrabalho.objects.create(
                mov_teletrabalho=mov_teletrabalho,
                observacao=observacao if observacao else MSG_DEFAULT_ATO_TELETRABALHO,
                acao="BLOQUEAR",
            )

            if anexo_id:
                anexo = Arquivo.objects.get(pk=anexo_id)
                historico.anexos.add(anexo)

            cancelar_solicitacao_aguardando_envio(
                mov_teletrabalho, observacao=observacao, status=status
            )

            enviar_notificacao_email_servidor(
                mov_teletrabalho, mov_teletrabalho.servidor, qtd_bloqueios
            )
            enviar_notificacao_email_servidor(
                mov_teletrabalho, mov_teletrabalho.aprovador, qtd_bloqueios
            )
    except Exception as e:
        log.error(e)
        raise Exception(e)


def concluir_mov_teletrabalho(mov_teletrabalho, observacao=None):
    """
    Rotina que finaliza o teletrabalho
    Args:
        mov_teletrabalho (obj): mov_teletrabalho.
        observacao (str).
    """
    try:
        with transaction.atomic():
            MovimentacaoTeletrabalho.objects.filter(pk=mov_teletrabalho.pk).update(
                situacao=STATUS_TELETRABALHO_CONCLUIDO,
            )
            HistoricoMovTeletrabalho.objects.create(
                mov_teletrabalho=mov_teletrabalho,
                observacao=observacao,
                acao="CONCLUIR",
            )
    except Exception as e:
        log.error(e)
        raise Exception(e)


def desbloquear_mov_teletrabalho(mov_teletrabalho, observacao=None):
    """
    Rotina que realiza o desbloqueio do teletrabalho
    Args:
        mov_teletrabalho (obj): mov_teletrabalho.
        observacao (str).
    """
    try:
        with transaction.atomic():
            MovimentacaoTeletrabalho.objects.filter(pk=mov_teletrabalho.pk).update(
                situacao=STATUS_TELETRABALHO_DESBLOQUEADO,
            )
            HistoricoMovTeletrabalho.objects.create(
                mov_teletrabalho=mov_teletrabalho,
                observacao=observacao,
                acao="DESBLOQUEAR",
            )
    except Exception as e:
        log.error(e)
        raise Exception(e)


def ignorar_mov_teletrabalho(mov_teletrabalho, observacao=None):
    """
    Rotina que ignora a movimentação do teletrabalho
    Args:
        mov_teletrabalho (obj): mov_teletrabalho.
        observacao (str).
    """
    try:
        with transaction.atomic():
            MovimentacaoTeletrabalho.objects.filter(pk=mov_teletrabalho.pk).update(
                situacao=STATUS_TELETRABALHO_IGNORADO,
            )
            HistoricoMovTeletrabalho.objects.create(
                mov_teletrabalho=mov_teletrabalho, observacao=observacao, acao="IGNORAR"
            )
    except Exception as e:
        log.error(e)
        raise Exception(e)


def verificar_plano_pendente_cancelamento(mov_teletrabalho, solicitacao):
    ultima_solicitacao = (
        SendingTelework.objects.filter(
            work_plan=mov_teletrabalho, cancelado_solicitacao=True
        )
        .order_by("reference_year", "reference_month")
        .last()
    )
    if ultima_solicitacao:
        if (
            ultima_solicitacao.reference_month == solicitacao.reference_month
            and ultima_solicitacao.reference_year == solicitacao.reference_year
        ):
            return True
    return False


def regularizar_mov_teletrabalho(solicitacao, observacao=None):
    """
    Rotina que regulariza a movimentação do teletrabalho
    Args:
        mov_teletrabalho (obj): mov_teletrabalho.
        observacao (str).
    """
    try:
        mov_teletrabalho = solicitacao.work_plan
        mes, ano = SendingTelework().get_reference_year_month(
            employee=solicitacao.employee
        )
        regularizar = False
        if mov_teletrabalho.situacao == STATUS_TELETRABALHO_PENDENTE:
            regularizar = verificar_plano_pendente_cancelamento(
                mov_teletrabalho, solicitacao
            )
        else:
            regularizar = verificar_referencia_enviada(solicitacao, mes, ano)

        if regularizar:
            with transaction.atomic():
                MovimentacaoTeletrabalho.objects.filter(pk=mov_teletrabalho.pk).update(
                    situacao=STATUS_TELETRABALHO_REGULAR,
                )
                HistoricoMovTeletrabalho.objects.create(
                    mov_teletrabalho=mov_teletrabalho,
                    observacao=observacao,
                    acao="REGULARIZAR",
                )
    except Exception as e:
        log.error(e)
        raise Exception(e)


def revogar_mov_teletrabalho(
    mov_teletrabalho, qtd_meses_impedido, data_fim, observacao=None
):
    """
    Rotina que realiza o revogação e encerramento do teletrabalho
    Args:
        mov_teletrabalho (obj): mov_teletrabalho.
        qtd_meses_impedido (int): Quantidade de meses impedido de pedir um novo teletrabalho.
        data_fim (date): data fim do teletrabalho
        observacao (str).
    """
    try:
        with transaction.atomic():
            mov_teletrabalho.situacao = STATUS_TELETRABALHO_REVOGADO
            mov_teletrabalho.qtd_meses_impedido = qtd_meses_impedido
            mov_teletrabalho.data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
            mov_teletrabalho.save()

            HistoricoMovTeletrabalho.objects.create(
                mov_teletrabalho=mov_teletrabalho, observacao=observacao, acao="REVOGAR"
            )
    except Exception as e:
        log.error(e)
        raise Exception(e)


def mov_status_teletrabalho_pendente(mov_teletrabalho, observacao=None):
    """
    Rotina que alterar a situação do teletrabalho para pedente após efetivar a
    solicitação de cancelamento do teletrabalho
    Args:
        mov_teletrabalho (obj): mov_teletrabalho
        observacao (str).
    """
    try:
        with transaction.atomic():
            MovimentacaoTeletrabalho.objects.filter(pk=mov_teletrabalho.pk).update(
                situacao=STATUS_TELETRABALHO_PENDENTE,
            )

            HistoricoMovTeletrabalho.objects.create(
                mov_teletrabalho=mov_teletrabalho,
                observacao=observacao,
                acao="PENDENTE",
            )
    except Exception as e:
        log.error(e)
        raise Exception(e)


def cancelar_solicitacao_aguardando_envio(
    mov_teletrabalho, observacao=None, status=None
):
    """
    Rotina que cancela a solicitação de teletrabalho aguardando envio
    Args:
        mov_teletrabalho (obj): mov_teletrabalho.
        observacao (str).
        status (int).
    """
    solicitacaoes_nao_enviada = mov_teletrabalho.pvf_work_plan.filter(
        status=STS_STAND_BY
    )
    msg = MSG_DEFAULT_ATO_TELETRABALHO
    observacao = observacao if observacao else msg
    status = status if status else STS_CANCELED_APPLICANT

    for solicitacao in solicitacaoes_nao_enviada:
        solicitacao.portalrequest_ptr.cancel(observation=observacao, status=status)


def verificar_plano_pendente(mov_teletrabalho, ultimo_envio):
    """
    Rotina que verifica se tem plano pendente de envio do relatório mensal
    Args:
        mov_teletrabalho (obj): mov_teletrabalho.
        ultimo_envio (obj): sending_telework.
    Returns:
        bool
    """
    if ultimo_envio:
        referencia_mes = ultimo_envio.reference_month
        referencia_ano = ultimo_envio.reference_year
        if (
            referencia_mes == mov_teletrabalho.data_fim.month
            and referencia_ano == mov_teletrabalho.data_fim.year
        ):
            return False
    return True


def verificar_referencia_enviada(ultimo_envio, mes, ano):
    """
    Rotina que verifica se já foi enviado o tele da referência passada
    Args:
        ultimo_envio (obj): sending_telework.
        mes (int): referência mês.
        ano (int): referência ano.
    Returns:
        bool
    """
    if ultimo_envio:
        if ultimo_envio.reference_month == mes and ultimo_envio.reference_year == ano:
            return True
    return False


def contar_dias_excluindo_afastamentos(
    data_inicio_intervalo, data_fim_intervalo, servidor
):
    """
    Rotina que retorna a qtd_dias de um período desconsiderando os afastamentos
    Args:
        data_inicio_intervalo (date): data inicio do intervalo.
        data_fim_intervalo (date):  data fim do intervalo.
        servidor (obj): objeto do servidor.
    Returns:
        int
    """
    afastamentos = BaseLicencaAfastamento.objects.filter(
        servidor=servidor,
        data_inicio__lte=data_fim_intervalo,
        data_fim__gte=data_inicio_intervalo,
    ).exclude(estado=CANCELED)

    total_dias = (data_fim_intervalo - data_inicio_intervalo).days + 1

    dias_a_subtrair = 0
    dias_afast_sem_recesso = 0

    ano_inicial = data_inicio_intervalo.year

    if data_inicio_intervalo.month == 1:
        ano_inicial = ano_inicial - 1

    dt_inicio_recesso = datetime(ano_inicial, 12, 20).date()
    dt_fim_recesso = datetime(ano_inicial + 1, 1, 6).date()

    tem_intersecao_recesso = intersercao_recesso(
        dt_inicio_recesso, dt_fim_recesso, data_inicio_intervalo, data_fim_intervalo
    )

    dias_recesso = qtde_dias_recesso(
        tem_intersecao_recesso,
        dt_inicio_recesso,
        dt_fim_recesso,
        data_inicio_intervalo,
        data_fim_intervalo,
    )

    for afastamento in afastamentos:
        inicio = max(data_inicio_intervalo, afastamento.data_inicio)
        fim = min(data_fim_intervalo, afastamento.data_fim)

        if tem_intersecao_recesso:
            dias_afast_sem_recesso = dias_afast_sem_recesso + subtrair_dias_intervalo(
                inicio, fim, dt_inicio_recesso, dt_fim_recesso
            )

        dias_a_subtrair += (fim - inicio).days + 1

    if tem_intersecao_recesso:
        dias_a_subtrair = dias_recesso + dias_afast_sem_recesso

    dias_uteis = total_dias - dias_a_subtrair
    return dias_uteis


def verificar_aguardando_envio_retorno(envio_tele_pendente, dt_corte_mes_subsquente):
    """
    Rotina que verifica se tem solicitação aguardando envio decorrente de retorno do aprovador
    Args:
        envio_tele_pendente (obj): envio do tele.
        dt_corte_mes_subsquente (date):  data de corte.
    Returns:
        int
    """
    ultimo_historico = (
        envio_tele_pendente.portalrequesthistory_set.last()
        if envio_tele_pendente
        else None
    )
    if ultimo_historico and ultimo_historico.date.date() > dt_corte_mes_subsquente:
        return True
    return False


def mov_teletrabalhos_pendentes(mov_teles, data_atual):
    """
    Rotina que os busca os teletrabalhos pendentes de envio
    Obs: Não considerar afastamentos e retornos da solicitação após a data de corte
    no caso de afastamentos somar dias sem contar com os afastamento. após somar 10 dias bloquear.
    Args:
        mov_tele (obj): movimentação do tele.
        data_atual (date):  data atual.
    Returns:
        int
    """
    mov_teletrabalhos_a_bloquear = []
    for mov_tele in mov_teles:
        ultimo_envio = (
            mov_tele.pvf_work_plan.exclude(
                status__in=[
                    STS_REJECTED,
                    STS_CANCELED_DGP,
                    STS_CANCELED_APPLICANT,
                    STS_STAND_BY,
                ]
            )
            .exclude(cancelado_solicitacao=True)
            .last()
        )

        envio_tele_pendente = (
            mov_tele.pvf_work_plan.filter(status=STS_STAND_BY)
            .exclude(cancelado_solicitacao=True)
            .last()
        )

        mes, ano = SendingTelework().get_reference_year_month(
            employee=mov_tele.servidor
        )
        mes_sub, ano_sub = proxima_referencia(mes, ano)
        dt_inicio_mes_subsquente = datetime(ano_sub, mes_sub, 1).date()
        dt_cadastro_plano = mov_tele.created_at.date()
        dt_inicio_mes_subsquente = (
            dt_cadastro_plano
            if dt_cadastro_plano > dt_inicio_mes_subsquente
            else dt_inicio_mes_subsquente
        )
        dt_corte_mes_subsquente = datetime(ano_sub, mes_sub, QTD_DIAS_BLOQUEIO).date()

        if (
            verificar_plano_pendente(mov_tele, ultimo_envio)
            and dt_inicio_mes_subsquente <= data_atual
            and not verificar_referencia_enviada(ultimo_envio, mes, ano)
        ):
            qtd_dias = contar_dias_excluindo_afastamentos(
                dt_inicio_mes_subsquente, data_atual, mov_tele.servidor
            )
            if qtd_dias > QTD_DIAS_BLOQUEIO and not verificar_aguardando_envio_retorno(
                envio_tele_pendente, dt_corte_mes_subsquente
            ):
                mov_teletrabalhos_a_bloquear.append(mov_tele)
    return mov_teletrabalhos_a_bloquear


def concluir_planos_teletrabalhos_sem_pendencias():

    movs_teletrabalhos = MovimentacaoTeletrabalho.objects.filter(
        ativo=False,
        situacao__in=[STATUS_TELETRABALHO_REGULAR],
    )
    for mov_teletrabalho in movs_teletrabalhos:
        ultimo_enviado = mov_teletrabalho.pvf_work_plan.filter(
            status=STS_EFFECTIVE
        ).last()
        if not verificar_plano_pendente(mov_teletrabalho, ultimo_enviado):
            concluir_mov_teletrabalho(mov_teletrabalho)
        log.info(f"Movimentação teletrabalho concluída: {mov_teletrabalho}")


def get_saldo_devedor(meta, mes, ano):
    """
    Rotina que busca o saldo devedor da meta na referência
    Args:
        meta(obj): meta do plano.
        mes (int): Mês de referência
        ano (int): Ano de referência
    Returns:
        int
    """
    saldo_devedor = 0
    meta_mensal = (
        MarkTelework.objects.filter(
            request__reference_month=mes, request__reference_year=ano, mark_plan=meta
        )
        .exclude(
            request__status__in=[STS_REJECTED, STS_CANCELED_DGP, STS_CANCELED_APPLICANT]
        )
        .last()
    )

    if meta_mensal:
        saldo_devedor = meta_mensal.saldo_devedor
    return saldo_devedor


def calculo_meta_mensal(meta, mes, ano, saldo_devedor):
    """
    Rotina que calcula a meta da referência
    considerando o saldo devedor da referência anterior e
    e os afastamentos no mês
    Args:
        meta(obj): meta do plano.
        mes (int): Mês de referência
        ano (int): Ano de referência
        saldo_devedor (int) saldo devedor do mês anterior
    Returns:
        int
    """
    servidor = meta.mov_teletrabalho.servidor
    dias_mes = calendar.monthrange(ano, mes)[1]
    dias_mes_proporcional = meta.meta_dias_mes(ano, mes)
    dias_afastamentos, dias_afastamento_diff_recesso = dias_afastamento_mes(
        servidor, mes, ano, meta
    )
    dias_nao_efetivo = abs((dias_afastamentos + (dias_mes - dias_mes_proporcional)))

    if mes == 1 or mes == 12:
        dt_inicio_recesso, dt_fim_recesso = datas_recesso_por_ano(ano, mes)

        if meta.data_fim >= dt_inicio_recesso:
            if meta.data_fim < dt_fim_recesso:
                dias_recesso = NewDateRange(dt_inicio_recesso, meta.data_fim).days
            else:
                dias_recesso = NewDateRange(dt_inicio_recesso, dt_fim_recesso).days

            dias_nao_efetivo = abs(
                (dias_afastamento_diff_recesso + dias_recesso)
                + (dias_mes - dias_mes_proporcional)
            )

    meta = round((meta.meta / dias_mes) * (dias_mes - dias_nao_efetivo))
    meta = meta + saldo_devedor
    return meta


def datas_recesso_por_ano(ano, mes):
    """
    Rotina que retorna a quantidade de dias de recesso do conforme o mês
    Args:
        mes (int): Mês de referência
        ano (int): Ano de referência
    Returns:
        [date, date]
    """
    if mes == 1:
        dt_inicio_recesso = datetime(ano, mes, 1).date()
        dt_fim_recesso = datetime(ano, mes, 6).date()
    else:
        dt_inicio_recesso = datetime(ano, mes, 20).date()
        dt_fim_recesso = datetime(ano, mes, 31).date()

    return dt_inicio_recesso, dt_fim_recesso


def dias_afastamento_sem_recesso(ano, mes, dt_inicio_afastamentro, dt_fim_afastamento):
    """
    Rotina que retorna a quantidade de dias do afastamento
    desconsiderando o dias de recesso
    Args:
        mes (int): Mês de referência
        ano (int): Ano de referência
        dt_inicio_afastamentro: date,
        dt_fim_afastamento: date
    Returns:
        int
    """
    dias_diff_afastamento = 0
    dt_inicio_recesso, dt_fim_recesso = datas_recesso_por_ano(ano, mes)
    intervalo_entre = NewDateRange.range_subtraction(
        [dt_inicio_afastamentro, dt_fim_afastamento],
        [dt_inicio_recesso, dt_fim_recesso],
    )

    if intervalo_entre:
        dias_diff_afastamento = NewDateRange(
            intervalo_entre[0][0], intervalo_entre[0][1]
        ).days
    return dias_diff_afastamento


def subtrair_dias_intervalo(dt_inicio, dt_fim, dt_inicio2, dt_fim2):
    """
    Rotina que subtrai os dias diferentes entre dois ranges de datas
    Args:
        dt_inicio: date
        dt_fim: date
        dt_inicio2: date
        dt_fim2: date
    Returns:
        int
    """
    dias_diff = 0
    intervalo_entre = NewDateRange.range_subtraction(
        [dt_inicio, dt_fim], [dt_inicio2, dt_fim2]
    )

    if intervalo_entre:
        dias_diff = NewDateRange(intervalo_entre[0][0], intervalo_entre[0][1]).days
    return dias_diff


def intersercao_recesso(inicio_recesso, fim_recesso, inicio_intervalo, fim_intervalo):
    """
    Rotina que verificar se existe se um intervalo de data tem
    interseção com os dias de recesso
    Args:
        inicio_recesso: date
        fim_recesso: date
        inicio_intervalo: date
        fim_intervalo: date
    Returns:
        bool
    """
    intersecao_data = NewDateRange.range_intersect(
        [inicio_recesso, fim_recesso], [inicio_intervalo, fim_intervalo]
    )

    intersecao_recesso = True if intersecao_data else False
    return intersecao_recesso


def qtde_dias_recesso(
    intersecao, inicio_recesso, fim_recesso, inicio_intervalo, fim_intervalo
):
    """
    Rotina que verificar se existe se um intervalo de data tem
    interseção com os dias de recesso
    Args:
        intersecao: bool
        inicio_recesso: date
        fim_recesso: date
        inicio_intervalo: date
        fim_intervalo: date
    Returns:
        bool
    """
    dias_recesso = QTD_DIAS_RECESSO
    dias_diff_recesso = 0
    if intersecao:
        dias_intervalo_recesso = NewDateRange.range_intersect(
            [inicio_recesso, fim_recesso], [inicio_intervalo, fim_intervalo]
        )

        if dias_intervalo_recesso:
            dias_diff_recesso = NewDateRange(
                dias_intervalo_recesso[0], dias_intervalo_recesso[1]
            ).days

        dias_recesso = dias_diff_recesso if dias_diff_recesso else QTD_DIAS_RECESSO
    return dias_recesso


def notificar_metas_com_saldo_devedor(solicitacao):
    metas_devedoras = solicitacao.pvf_request_telework.filter(saldo_devedor__gt=0)
    if metas_devedoras.exists():
        enviar_notificacao_saldo_devedor(metas_devedoras)


def zerar_saldo_devedor(mov_teletrabalho, observacao=None, anexo_id=None):
    """
    Função utilitária para zerar o saldo devedor dos registros relacionados a um MovimentacaoTeletrabalho.
    """
    try:
        status_aguardando_envio = 9
        status_cancelado = 7
        status_aguardando_aprovador = 2

        ultimo_request = (
            SendingTelework.objects.filter(
                work_plan=mov_teletrabalho, cancelado_solicitacao=False
            )
            .exclude(
                status__in=[
                    status_aguardando_envio,
                    status_cancelado,
                    status_aguardando_aprovador,
                ]
            )
            .last()
        )

        if not ultimo_request:
            return {
                "success": False,
                "message": "Nenhum SendingTelework não cancelado encontrado.",
            }

        aguardando_request = SendingTelework.objects.filter(
            work_plan=mov_teletrabalho,
            cancelado_solicitacao=False,
            status=status_aguardando_envio,
        ).last()

        mark_teleworks = MarkTelework.objects.filter(
            request=ultimo_request, saldo_devedor__gt=0
        )

        if not mark_teleworks.exists():
            return {
                "success": False,
                "message": "Nenhum saldo devedor encontrado para o plano.",
            }

        with transaction.atomic():
            mark_teleworks.update(saldo_devedor=0)

            if aguardando_request:
                mark_teleworks_aguardando = MarkTelework.objects.filter(
                    request=aguardando_request,
                )
                mark_teleworks_aguardando.update(saldo_devedor_anterior=0)

            historico = HistoricoMovTeletrabalho.objects.create(
                mov_teletrabalho=mov_teletrabalho,
                observacao=observacao if observacao else MSG_DEFAULT_ATO_TELETRABALHO,
                acao="ZERAR",
            )

            if anexo_id:
                anexo = Arquivo.objects.get(pk=anexo_id)
                historico.anexos.add(anexo)

            atualizar_possui_saldo_devedor(mov_teletrabalho)

        return {
            "success": True,
            "message": "Saldo devedor zerado com sucesso.",
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
        }


def atualizar_possui_saldo_devedor(movimentacao):
    """
    Atualiza o campo 'possui_saldo_devedor' para uma movimentação de teletrabalho específica
    ou para todas as movimentações ativas, se nenhuma for passada.

    Args:
        movimentacao (MovimentacaoTeletrabalho): A movimentação específica a ser atualizada.
    """
    try:
        ultimo_envio = (
            SendingTelework.objects.filter(
                work_plan=movimentacao,
                status=4,  # Efetivado
                cancelado_solicitacao=False,
            )
            .order_by("-id")
            .first()
        )

        if not ultimo_envio:
            return {
                "success": False,
                "message": "Nenhum SendingTelework não cancelado encontrado.",
            }

        has_saldo_devedor = MarkTelework.objects.filter(
            request=ultimo_envio, saldo_devedor__gt=0
        ).exists()

        movimentacao.possui_saldo_devedor = has_saldo_devedor
        movimentacao.save()

        return {"success": True, "message": "Saldo devedor atualizado com sucesso."}

    except Exception as e:
        return {"success": False, "message": f"Ocorreu um erro: {str(e)}"}


def dias_teletrabalho_mes(mes, ano, servidor):
    """
    Retorna uma lista de dias de teletrabalho no mês
    Args:
        ano (int): O ano.
        mes (int): O mês (1 a 12).
        servidor (objeto): objeto do servidor
    Returns:
        list: lista de dias de teletrabalho no mês
    """

    dias_uteis = dias_uteis_no_mes(ano, mes)
    inicio, fim = data_inicio_fim_referencia(mes, ano)
    movteletrabalhos = MovimentacaoTeletrabalho.objects.filter(
        data_inicio__lte=fim, data_fim__gte=inicio, servidor=servidor
    )
    datas_teletrabalho = []
    for movteletrabalho in movteletrabalhos:
        data_fim = movteletrabalho.data_fim
        data_inicio = movteletrabalho.data_inicio
        for dia in dias_uteis:
            if data_inicio <= dia and data_fim >= dia:
                datas_teletrabalho.append(dia)
    return datas_teletrabalho


def dias_uteis_no_mes(ano, mes):
    """
    Retorna uma lista de dias úteis em um mês, considerando feriados
    Args:
        ano (int): O ano.
        mes (int): O mês (1 a 12).
    Returns:
        list: lista do dias do mês
    """
    _, n_dias_no_mes = calendar.monthrange(ano, mes)
    dias_uteis = []
    for dia in range(1, n_dias_no_mes + 1):
        data = datetime(ano, mes, dia).date()
        if data.weekday() < 5 and data:
            dias_uteis.append(data)

    return dias_uteis
