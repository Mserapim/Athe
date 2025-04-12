from calendar import monthrange
from datetime import timedelta
from contrib.base_converter import formatar_hora_timedelta
from contrib.daterange import NewDateRange
from common.usefulday.models import NonWorkingDay
from contrib.middleware import get_current_user
from rh.const import CANCELED
from rh.dayoff.const import USU_NEW, USU_SUBSTITUTE
from rh.dayoff.models import Usufruct
from rh.models import CargaHoraria, MovimentacaoTeletrabalho, ServidorLotacao
from rh.pvf.apiv2.utils.approval import belongs_group_dgp
from rh.pvf.const import (
    ABRANGENCY_CITY,
    STS_CANCELED_APPLICANT,
    STS_CANCELED_DGP,
    STS_EFFECTIVE,
    STS_REJECTED,
)
from rh.pvf.models import PortalRequest, PortalRequestAbsence
from rh.registerpoint.const import (
    DIAS_SEMANA,
    DSR,
    FALTA,
    FERIADOS_PONTO_FACULTATIVOS,
    JUSTIFICADO,
    LICENCAS_AFASTAMENTOS,
    NORMAL,
    TIPO_DIA,
    VIAGEM_A_SERVICO,
    TELETRABALHO,
    STATUS_RELATORIO_JUST_PONTO,
)
from rh.pvf.utils.folha_ponto import data_inicio_fim_referencia
from rh.registerpoint.const import (
    DIAS_SEMANA,
    DSR,
    FALTA,
    FERIADOS_PONTO_FACULTATIVOS,
    JUSTIFICADO,
    LICENCAS_AFASTAMENTOS,
    NORMAL,
    TIPO_DIA,
)
from rh.registerpoint.models import MarkPoint
from django.db.models.query_utils import Q
from rh.afastamento.models import BaseLicencaAfastamento
from contrib.utils import employee_from_user, getLogger
from itertools import groupby
from collections import defaultdict
from datetime import datetime
from rh.pvf.models import PointJustification


from standard.models import JustificationItem


log = getLogger(__name__)


def localidade_servidor(servidor, dt_inicio, dt_fim):
    """
    Retorna uma lista de localidades (cidades) do servidor no período especificado
    Args:
        servidor (object)
        dt_inicio (date): período início
        dt_fim (date): período fim
    Returns:
        list: lista de localidades ids
    """
    lotacoes = ServidorLotacao.objects.filter(
        servidor=servidor, designacao=False
    ).filter(
        Q(data_vigencia_inicio__lte=dt_fim)
        & (Q(data_vigencia_fim__isnull=True) | Q(data_vigencia_fim__gte=dt_inicio))
    )

    localidades = []
    for lotacao in lotacoes:
        inicio = max(lotacao.data_vigencia_inicio, dt_inicio)
        fim = min(lotacao.data_vigencia_fim or dt_fim, dt_fim)
        localidades.append(
            {
                "localidade_id": lotacao.lotacao.localidade_id,
                "inicio": inicio,
                "fim": fim,
            }
        )

    return localidades


def total_horas_marcacoes(marcacoes):
    """
    Retorna total de horas de marcações no mês
    Args:
        marcacoes (list): lista de marcações
    Returns:
        timedelta: total de marcaçoes no mês
    """
    saldo = timedelta(0)
    grupo_por_data = {}
    for date, grupo in groupby(marcacoes, key=lambda x: x.date()):
        grupo_por_data[date] = list(grupo)
    for grupo in grupo_por_data:
        lista_marcacao = grupo_por_data[grupo]
        if verifica_indice(0, lista_marcacao) and verifica_indice(1, lista_marcacao):
            diferenca_time = lista_marcacao[1] - lista_marcacao[0]
            saldo = saldo + diferenca_time
        if verifica_indice(2, lista_marcacao) and verifica_indice(3, lista_marcacao):
            diferenca_time = lista_marcacao[3] - lista_marcacao[2]
            saldo = saldo + diferenca_time
        if verifica_indice(4, lista_marcacao) and verifica_indice(5, lista_marcacao):
            diferenca_time = lista_marcacao[4] - lista_marcacao[5]
            saldo = saldo + diferenca_time
    return saldo


def carga_horaria_diaria(jornadas_trabalho, dia):
    """
    Retorna a carga horária diária
    Args:
        servidor (objeto): objeto do servidor
    Returns:
        int: carga horária diária
    """
    try:
        for jornada in jornadas_trabalho:
            if jornada.data_inicio and jornada.data_fim:
                if (
                    jornada.data_inicio <= dia
                    and jornada.data_fim >= dia
                    and jornada.jornada_trabalho
                ):
                    return int(jornada.jornada_trabalho.duration_hour)
            elif jornada.data_inicio <= dia and jornada.jornada_trabalho:
                return int(jornada.jornada_trabalho.duration_hour)

        raise Exception("Servidor sem jornada de trabalho no período especificado.")
    except Exception as err:
        log.error(err)
        raise


def verifica_indice(indice, lista):
    """
    Verifica se o indice existe na lista
    Args:
        indice (int): O ano.
        lista (list): lista de datas
    Returns:
        bool: se o indice existe na lista
    """
    if 0 <= indice < len(lista):
        return True
    return False


def inicio_fim_competencia(mes, ano):
    """
    Retorna da data inicio e fim do mês
    Args:
        mes (int): período mês.
        ano (int): período ano.
    Returns:
        list: (dt_inicio, dt_fim)
    """
    hoje = datetime.today().date()
    if mes and ano:
        mes, ano = [int(mes), int(ano)]
        inicio = datetime(ano, mes, 1).date()
        fim = datetime(ano, mes, monthrange(ano, mes)[1]).date()
        return inicio, fim
    inicio = datetime(hoje.year, hoje.month, 1).date()
    fim = datetime(hoje.year, hoje.month, monthrange(hoje.year, hoje.month)[1]).date()
    return inicio, fim


def dias_feriados(dt_inicio, dt_fim, servidor):
    """
    Retorna uma lista feriados do período
    Args:
        dt_inicio (date): período inicio.
        dt_fim (date): período fim.
        servidor (objeto): objeto do servidor
    Returns:
        list: lista dias(feriados)
    """
    feriados = NonWorkingDay.objects.filter(
        start_date__range=[dt_inicio, dt_fim]
    ).exclude(is_partial=True)
    localidades = localidade_servidor(servidor, dt_inicio, dt_fim)
    feriados_por_data = defaultdict(list)

    for localidade in localidades:
        local_id = localidade["localidade_id"]
        local_inicio = localidade["inicio"]
        local_fim = localidade["fim"]

        for feriado in feriados:
            if not (local_inicio <= feriado.start_date.date() <= local_fim):
                continue

            if feriado.abrangency == ABRANGENCY_CITY:
                if feriado.places.filter(pk=local_id).exists():
                    if feriado.end_date and feriado.kind == 4:  # Recesso
                        feriado_dia_a_dia(feriado, feriados_por_data)
                    else:
                        feriados_por_data[feriado.start_date.date()].append(
                            feriado.description
                        )
            else:
                if feriado.end_date and feriado.kind == 4:  # Recesso
                    feriado_dia_a_dia(feriado, feriados_por_data)
                else:
                    feriados_por_data[feriado.start_date.date()].append(
                        feriado.description
                    )

    return feriados_por_data


def feriado_dia_a_dia(feriado, feriados_por_data):
    date_range = NewDateRange(feriado.start_date.date(), feriado.end_date.date())
    for dia in date_range.iter():
        feriados_por_data[dia].append(feriado.description)

    return feriados_por_data


def infos_por_data(inicio, fim, texto, itens_por_data):
    """
    Retorna itens separados por data
    Args:
        inicio (date): período inicio.
        fim (date): período fim.
        texto (str): descrição
        itens_por_data: dict
    Returns:
        dict: lista de marcações do período
    """
    n_dias = (fim - inicio).days + 1
    for i in range(n_dias):
        data = inicio + timedelta(days=i)
        itens_por_data[data] = texto
    return itens_por_data


def marcacoes_dias(dt_inicio, dt_fim, servidor):
    """
    Retorna as marcações do mês folha ponto
    Args:
        dt_inicio (date): período inicio.
        dt_fim (date): período fim.
        servidor (objeto): objeto do servidor
    Returns:
        list: lista de marcações do período
    """
    marcacoes = MarkPoint.objects.filter(
        Q(marcacao__range=[dt_inicio, dt_fim]) | Q(day__range=[dt_inicio, dt_fim]),
        Q(employee=servidor),
    ).order_by("marcacao")

    marcacoes_por_data = defaultdict(list)
    for ponto in marcacoes:
        if ponto.marcacao:
            editado_por = None
            servidor_modificador = None

            created_at = ponto.created_at.replace(microsecond=0)
            modified_at = ponto.modified_at.replace(microsecond=0)

            if created_at != modified_at:
                if ponto.modified_by:
                    servidor_modificador = employee_from_user(ponto.modified_by)
                    if servidor_modificador:
                        if servidor_modificador == ponto.employee:
                            editado_por = "servidor"
                        elif servidor_modificador.user.groups.filter(
                            name="mpmt-perfil-vdf-aprovador-servidores"
                        ).exists():
                            editado_por = "DGP"
                        else:
                            editado_por = "chefia"

            marcacoes_por_data[ponto.marcacao.date()].append(
                {
                    "id": ponto.id,
                    "marcacao": ponto.marcacao,
                    "marcacao_hora": ponto.marcacao.time(),
                    "marcacao_valida": ponto.marcacao_valida,
                    "editado_por": editado_por,
                    "editado_por_nome": (
                        servidor_modificador.pessoa_fisica.nome
                        if servidor_modificador
                        else None
                    ),
                }
            )
    return marcacoes_por_data


def dias_justificados(dt_inicio, dt_fim, servidor, relatorio=False):
    """
    Retorna as justificavas da marcação folha ponto
    Args:
        dt_inicio (date): período inicio.
        dt_fim (date): período fim.
        servidor (obj):
    Returns:
        list: lista das justificavas no período
    """

    status_filtro = STATUS_RELATORIO_JUST_PONTO if relatorio else [STS_EFFECTIVE]

    justiticativas = PointJustification.objects.filter(
        Q(
            request__isnull=False,
            cancelado=False,
            employee=servidor,
            request__status__in=status_filtro,
            start_date__lte=dt_fim,
            end_date__gte=dt_inicio,
        )
        | Q(
            request__isnull=True,
            cancelado=False,
            employee=servidor,
            start_date__lte=dt_fim,
            end_date__gte=dt_inicio,
        )
    )
    justificativas_por_data = defaultdict(list)
    for justificativa in justiticativas:
        justificativa_texto = JustificationItem.objects.get(
            value=justificativa.reason_type
        ).name
        infos_por_data(
            justificativa.start_date,
            justificativa.end_date,
            justificativa_texto,
            justificativas_por_data,
        )
    return justificativas_por_data


def dias_afastamento(dt_inicio, dt_fim, servidor):
    """
    Retorna os afastamentos informados no período folha ponto
    Args:
        dt_inicio (date): período inicio.
        dt_fim (date): período fim.
        servidor (obj):
    Returns:
        afastamentos por data
    """
    afastamentos = BaseLicencaAfastamento.objects.filter(
        Q(data_inicio__lte=dt_fim) & Q(data_fim__gte=dt_inicio), Q(servidor=servidor)
    ).exclude(estado__in=[CANCELED])
    afastamentos_por_data = defaultdict(list)
    for afastamento in afastamentos:
        afastamento_label = afastamento.situation_unicode
        infos_por_data(
            afastamento.data_inicio,
            afastamento.data_fim,
            afastamento_label,
            afastamentos_por_data,
        )
    return afastamentos_por_data


def dias_afastamento_pendente(dt_inicio, dt_fim, servidor):
    """
    Retorna os afastamentos pendentes de aprovação no período folha ponto
    Args:
        dt_inicio (date): período inicio.
        dt_fim (date): período fim.
        servidor (obj):
    Returns:
        afastamentos pendentes por data
    """
    afastamentos = PortalRequestAbsence.objects.filter(
        Q(start_date__lte=dt_fim) & Q(end_date__gte=dt_inicio), Q(employee=servidor)
    ).exclude(
        status__in=[
            STS_CANCELED_DGP,
            STS_CANCELED_APPLICANT,
            STS_REJECTED,
            STS_EFFECTIVE,
        ]
    )

    usufrutos = Usufruct.objects.filter(
        Q(start_date__lte=dt_fim) & Q(end_date__gte=dt_inicio),
        Q(
            activity__acquisition_period__employee=servidor,
            status__in=[USU_NEW, USU_SUBSTITUTE],
        ),
    )

    afastamentos_por_data = defaultdict(list)

    for afastamento in afastamentos:
        afastamento_label = (
            f"{afastamento.type_of_request} - {afastamento.get_status_display()}"
        )
        infos_por_data(
            afastamento.start_date,
            afastamento.end_date,
            afastamento_label,
            afastamentos_por_data,
        )

    for usufruto in usufrutos:
        usufruto_label = f"""{usufruto.activity.configuration.get_sub_type_of_usufruct_display()} - 
            {usufruto.get_status_display()}"""
        infos_por_data(
            usufruto.start_date,
            usufruto.end_date,
            usufruto_label,
            afastamentos_por_data,
        )

    return afastamentos_por_data


def dias_viagem(dt_inicio, dt_fim, servidor):
    """
    Retorna os dias que o servidor esteve em viagem a serviço no período especificado.
    Args:
        dt_inicio (date): período início.
        dt_fim (date): período fim.
        servidor (obj): objeto do servidor.
    Returns:
        dict: dias de viagem a serviço por data.
    """
    from diarias.models import Beneficiario

    fluxo_rascunho = 2
    fluxo_cancelado = 32
    fluxo_cancelado_daa = 34
    fluxo_cancelado_deplan = 35
    fluxo_indeferido = 21

    beneficiarios = (
        Beneficiario.objects.filter(
            servidor=servidor,
            viagem__data_inicio_viagem__lte=dt_fim,
            viagem__data_fim_viagem__gte=dt_inicio,
        )
        .exclude(
            fluxo__id__in=[
                fluxo_rascunho,
                fluxo_cancelado,
                fluxo_cancelado_daa,
                fluxo_cancelado_deplan,
                fluxo_indeferido,
            ]
        )
        .select_related("viagem")
        .prefetch_related("destinos", "calculos_diarias_consolidados")
    )

    dias_viagem = defaultdict(list)

    for beneficiario in beneficiarios:

        if beneficiario.viagem.importada:
            datas = list(
                set(
                    destino.data.date()
                    for destino in beneficiario.destinos.order_by("data").all()
                )
            )

            for data in datas:
                if dt_inicio <= data <= dt_fim:
                    dias_viagem[data].append("Viagem a Serviço")
        else:
            destinos = sorted(
                beneficiario.destinos.all(),
                key=lambda destino: destino.data_daa or destino.data,
            )

            if not destinos:
                continue

            data_inicio_viagem = (
                destinos[0].data_daa.date()
                if destinos[0].data_daa
                else destinos[0].data.date()
            )
            calculo = getattr(beneficiario, "calculos_diarias_consolidados", None)
            qtd_diarias = calculo.qtd_total_diarias_deferido if calculo else 0

            if not qtd_diarias or qtd_diarias <= 0:
                continue

            dias = [
                data_inicio_viagem + timedelta(days=i) for i in range(int(qtd_diarias))
            ]
            if qtd_diarias % 1 != 0:
                dias.append(data_inicio_viagem + timedelta(days=int(qtd_diarias)))

            for dia in dias:
                if dt_inicio <= dia <= dt_fim:
                    dias_viagem[dia].append("Viagem a Serviço")

    return dias_viagem


def dias_teletrabalho(dt_inicio, dt_fim, servidor):
    """
    Retorna os dias em que o servidor esteve em teletrabalho no período especificado.
    Args:
        dt_inicio (date): período início.
        dt_fim (date): período fim.
        servidor (obj): objeto do servidor.
    Returns:
        dict: dias de teletrabalho por data.
    """
    from rh.models import MovimentacaoTeletrabalho

    movimentacoes = MovimentacaoTeletrabalho.objects.filter(
        servidor=servidor, data_inicio__lte=dt_fim, data_fim__gte=dt_inicio
    )

    dias_teletrabalho = defaultdict(list)

    for movimentacao in movimentacoes:
        data_inicio = max(movimentacao.data_inicio, dt_inicio)
        data_fim = min(movimentacao.data_fim or dt_fim, dt_fim)

        dias = [
            data_inicio + timedelta(days=i)
            for i in range((data_fim - data_inicio).days + 1)
        ]

        for dia in dias:
            dias_teletrabalho[dia].append("Teletrabalho")

    return dias_teletrabalho


def saldo_dia(ch_dia, total_marcacoes):
    """
    Retorna o saldo diário folha ponto
    Args:
        ch_dia (int) Carga horária dia
        total_marcacoes (int):total do saldo de maracaoes dia
    Returns:
        bool
    """
    carga_horaria_delta = timedelta(hours=ch_dia)
    if total_marcacoes < carga_horaria_delta:
        saldo = carga_horaria_delta - total_marcacoes
        saldo_str = f"-{formatar_hora_timedelta(saldo)}"
    else:
        saldo = total_marcacoes - carga_horaria_delta
        saldo_str = formatar_hora_timedelta(saldo)
    return saldo_str


def marcacao_editavel(perfil_dgp, responsavel, servidor_logado, servidor, dia):
    """
    Retorna se o dia é editável para ignorar batida
    Args:
        perfil_dgp (bool)
        responsavel: (bool).
        servidor_logado (objeto servidor)
        servidor (objeto servidor)
        dia (date):
    Returns:
        bool
    """
    from rh.pvf.models import SendingTimeSheet

    hoje = datetime.today().date()

    existe_sending = (
        SendingTimeSheet.objects.filter(
            employee=servidor,
            reference_month=dia.month,
            reference_year=dia.year,
        )
        .exclude(status__in=[STS_REJECTED, STS_CANCELED_DGP, STS_CANCELED_APPLICANT])
        .exists()
    )

    if not existe_sending:
        mesmo_servidor = servidor_logado == servidor and hoje == dia
        return perfil_dgp or responsavel or mesmo_servidor
    return False


def dict_marcacoes(params):
    """
    Retorna um dict com as marcações agrupadas por dia
    Args:
       params:(dia,feriados, marcacoes, justificativas, afastamentos, servidor,
       ch_dia,editavel, afastamentos_pendentes)
    Returns:
        objeto da marcações mensais
    """
    dia = params.get("dia")
    ch_dia = params.get("ch_dia")
    feriado_dia = params.get("feriados").get(dia, [])
    marcacoes_dia = params.get("marcacoes").get(dia, [])
    justificativa_dia = params.get("justificativas").get(dia, [])
    afastamento_dia = params.get("afastamentos").get(dia, [])
    viagens_dia = params.get("viagens").get(dia, [])
    teletrabalho_dia = params.get("teletrabalho").get(dia, [])
    dia_semana = dia.weekday()
    dia_formatado = dia.strftime("%d/%m/%Y")
    editavel = params.get("editavel", False)
    afastamento_pendente = params.get("afastamentos_pendentes").get(dia, None)
    marcacoes_lista = [
        item.pop("marcacao")
        for item in marcacoes_dia
        if item.get("marcacao_valida", True)
    ]
    marcacoes_validas = any(m.get("marcacao_valida", True) for m in marcacoes_dia)

    if feriado_dia:
        if isinstance(feriado_dia, list):
            feriado_texto = (
                feriado_dia[0] if len(feriado_dia) == 1 else ", ".join(feriado_dia)
            )
        else:
            feriado_texto = feriado_dia
        return {
            "data": dia_formatado,
            "dia": DIAS_SEMANA[dia_semana],
            "tipo": FERIADOS_PONTO_FACULTATIVOS,
            "tipo_texto": feriado_texto,
            "marcacoes": marcacoes_dia,
            "total_dia": None,
            "saldo_dia": None,
            "carga_horaria": formatar_hora_timedelta(timedelta(hours=ch_dia)),
            "editavel": False,
            "afastamento_pendente": afastamento_pendente,
        }
    elif afastamento_dia:
        return {
            "data": dia_formatado,
            "dia": DIAS_SEMANA[dia_semana],
            "tipo": LICENCAS_AFASTAMENTOS,
            "tipo_texto": afastamento_dia,
            "marcacoes": marcacoes_dia,
            "total_dia": formatar_hora_timedelta(timedelta(hours=ch_dia)),
            "saldo_dia": formatar_hora_timedelta(timedelta(hours=0)),
            "carga_horaria": formatar_hora_timedelta(timedelta(hours=ch_dia)),
            "editavel": False,
            "afastamento_pendente": afastamento_pendente,
        }
    elif viagens_dia:
        return {
            "data": dia_formatado,
            "dia": DIAS_SEMANA[dia_semana],
            "tipo": VIAGEM_A_SERVICO,
            "tipo_texto": "Viagem a serviço",
            "marcacoes": marcacoes_dia,
            "total_dia": formatar_hora_timedelta(timedelta(hours=ch_dia)),
            "saldo_dia": formatar_hora_timedelta(timedelta(hours=0)),
            "carga_horaria": formatar_hora_timedelta(timedelta(hours=ch_dia)),
            "editavel": False,
            "afastamento_pendente": afastamento_pendente,
        }
    elif justificativa_dia:
        return {
            "data": dia_formatado,
            "dia": DIAS_SEMANA[dia_semana],
            "tipo": JUSTIFICADO,
            "tipo_texto": justificativa_dia,
            "marcacoes": marcacoes_dia,
            "total_dia": formatar_hora_timedelta(timedelta(hours=ch_dia)),
            "saldo_dia": formatar_hora_timedelta(timedelta(hours=0)),
            "carga_horaria": formatar_hora_timedelta(timedelta(hours=ch_dia)),
            "editavel": False,
            "afastamento_pendente": afastamento_pendente,
        }
    elif marcacoes_dia and marcacoes_validas:
        return {
            "data": dia_formatado,
            "dia": DIAS_SEMANA[dia_semana],
            "tipo": NORMAL,
            "tipo_texto": TIPO_DIA.get(NORMAL),
            "marcacoes": marcacoes_dia,
            "total_dia": formatar_hora_timedelta(
                total_horas_marcacoes(marcacoes_lista)
            ),
            "saldo_dia": saldo_dia(ch_dia, total_horas_marcacoes(marcacoes_lista)),
            "carga_horaria": formatar_hora_timedelta(timedelta(hours=ch_dia)),
            "editavel": editavel,
            "afastamento_pendente": afastamento_pendente,
        }
    elif dia_semana >= 5:
        return {
            "data": dia_formatado,
            "dia": DIAS_SEMANA[dia_semana],
            "tipo": DSR,
            "tipo_texto": TIPO_DIA.get(DSR),
            "marcacoes": marcacoes_dia,
            "total_dia": None,
            "saldo_dia": None,
            "carga_horaria": formatar_hora_timedelta(timedelta(hours=ch_dia)),
            "editavel": False,
            "afastamento_pendente": afastamento_pendente,
        }
    elif teletrabalho_dia:
        return {
            "data": dia_formatado,
            "dia": DIAS_SEMANA[dia_semana],
            "tipo": TELETRABALHO,
            "tipo_texto": teletrabalho_dia[0],
            "marcacoes": marcacoes_dia,
            "total_dia": formatar_hora_timedelta(timedelta(hours=ch_dia)),
            "saldo_dia": formatar_hora_timedelta(timedelta(hours=0)),
            "carga_horaria": formatar_hora_timedelta(timedelta(hours=ch_dia)),
            "editavel": False,
            "afastamento_pendente": afastamento_pendente,
        }
    else:
        return {
            "data": dia_formatado,
            "dia": DIAS_SEMANA[dia_semana],
            "tipo": FALTA,
            "tipo_texto": TIPO_DIA.get(FALTA),
            "marcacoes": marcacoes_dia,
            "total_dia": formatar_hora_timedelta(timedelta(hours=0)),
            "saldo_dia": formatar_hora_timedelta(timedelta(hours=-ch_dia)),
            "carga_horaria": formatar_hora_timedelta(timedelta(hours=ch_dia)),
            "editavel": False,
            "afastamento_pendente": afastamento_pendente,
        }


def folha_ponto_periodo(
    dt_inicio, dt_fim, servidor, usuario_logado=None, tipos_dia=[], relatorio=False
):
    """
    Retorna o folha ponto do mês
    Args:
        dt_inicio (date): período inicio.
        dt_fim (date): período fim.
        servidor (obj):
        tipos_dia (list):
    Returns:
        objeto da marcações mensais
    """
    dt_inicio, dt_fim = get_data_inicio_fim_ponto(servidor, dt_inicio, dt_fim)
    hoje = datetime.today().date()
    dias_intervalo = [
        (dt_inicio + timedelta(days=i))
        for i in range((dt_fim - dt_inicio).days + 1)
        if (dt_inicio + timedelta(days=i)) <= hoje
    ]
    folha_ponto = []
    feriados = dias_feriados(dt_inicio, dt_fim, servidor)
    marcacoes = marcacoes_dias(dt_inicio, dt_fim, servidor)
    justificativas = dias_justificados(dt_inicio, dt_fim, servidor, relatorio=relatorio)
    afastamentos = dias_afastamento(dt_inicio, dt_fim, servidor)
    afastamentos_pendentes = dias_afastamento_pendente(dt_inicio, dt_fim, servidor)
    viagens = dias_viagem(dt_inicio, dt_fim, servidor)
    teletrabalho = dias_teletrabalho(dt_inicio, dt_fim, servidor)
    jornadas_trabalho = CargaHoraria.objects.filter(
        servidor=servidor, jornada_trabalho__isnull=False
    ).order_by("-data_inicio")
    servidor_logado = (
        employee_from_user(get_current_user())
        if not usuario_logado
        else employee_from_user(usuario_logado)
    )
    perfil_dgp = True if belongs_group_dgp(servidor_logado) else False
    responsavel = get_responsavel(servidor)
    for dia in dias_intervalo:
        editavel = marcacao_editavel(
            perfil_dgp, responsavel, servidor_logado, servidor, dia
        )
        ch_dia = carga_horaria_diaria(jornadas_trabalho, dia)
        params = {
            "dia": dia,
            "feriados": feriados,
            "marcacoes": marcacoes,
            "justificativas": justificativas,
            "afastamentos": afastamentos,
            "viagens": viagens,
            "teletrabalho": teletrabalho,
            "servidor": servidor,
            "ch_dia": ch_dia,
            "editavel": editavel,
            "afastamentos_pendentes": afastamentos_pendentes,
        }
        marcacoes_dia = dict_marcacoes(params)
        if not tipos_dia:
            folha_ponto.append(marcacoes_dia)
        elif marcacoes_dia.get("tipo") in tipos_dia:
            folha_ponto.append(marcacoes_dia)

    return folha_ponto


def servidores_chefe_imediato(chefe):
    """
    Retorna os servidores da lotação onde o responsavel é difirente do chefe imediato
    Args:
        chefe: (servidor) chefe imediato
    Returns:
        list: lista de pks de servidores
    """
    subordinados_pks = []
    servidores_subordinados = chefe.subordinados.filter(ativo=True).distinct()
    for servidor_subordinado in servidores_subordinados:
        lotacao_subordinado = servidor_subordinado.workplace_current
        if lotacao_subordinado and lotacao_subordinado.responsavel != chefe:
            if not chefe.afastamento_ativo():
                subordinados_pks.append(servidor_subordinado.pk)
    return subordinados_pks


def inserir_pks_servidores(lotacao, subordinados_pks):
    """
    Função que inseri os pks a lista de subornidados
    Args:
        lotacao: (objeto)
        subordinados_pks: list
    """
    servidores_pks = (
        lotacao.servidores_lotacao.filter(ativo=True)
        .order_by("servidor__pk")
        .distinct("servidor__pk")
        .exclude(servidor__type_by_possession__in=["MBR", "MEL", "MEC"])
        .values_list("servidor__pk", flat=True)
    )

    subordinados_pks.extend(list(servidores_pks))


def servidores_aprovador_portal(chefe):
    """
    Retorna os servidores da lotação aprovador portal
    Args:
        chefe: (servidor) chefe imediato
    Returns:
        list: lista de pks de servidores
    """
    subordinados_pks = []
    servidores_lotacoes = chefe.responsible().filter(lotacao__portal_approver=True)
    for servidor_lotacao in servidores_lotacoes:
        lotacoes_subordinadas = servidor_lotacao.lotacao.lotacoes_subordinadas.filter(
            portal_approver=False
        )
        inserir_pks_servidores(servidor_lotacao.lotacao, subordinados_pks)

        for lotacao_subordinada in lotacoes_subordinadas:
            inserir_pks_servidores(lotacao_subordinada, subordinados_pks)
    return subordinados_pks


def get_responsavel(servidor):
    """
    Retorna se o servidor logado é aprovador
    Args:
        servidor: (objeto)
    Returns:
        bool
    """
    responsavel = False
    try:
        instancia_solicitacao = PortalRequest()
        responsavel_servidor = instancia_solicitacao.get_immediate_boss(servidor)
        if responsavel_servidor == employee_from_user(get_current_user()):
            responsavel = True
    except:
        log.error("Não foi possível encontrar um aprovador.")
    return responsavel


def get_lotacoes_aprovador(servidor):
    lotacoes_pk = []
    servidores_lotacoes = servidor.responsible().filter(lotacao__portal_approver=True)
    for servidor_lotacao in servidores_lotacoes:
        lotacoes_pk.append(servidor_lotacao.lotacao.pk)
        lotacoes_pk.extend(
            list(
                servidor_lotacao.lotacao.lotacoes_subordinadas.values_list(
                    "pk", flat=True
                )
            )
        )
    return lotacoes_pk


def total_faltas_e_saldo_periodo(mes, ano, servidor):
    inicio, fim = data_inicio_fim_referencia(mes, ano)
    dados_ponto = folha_ponto_periodo(inicio, fim, servidor)
    qtd_faltas = 0
    saldo_dia_total = timedelta(0)
    for dia in dados_ponto:
        try:
            if dia["saldo_dia"] is not None:
                negativo = dia["saldo_dia"].startswith("-")
                saldo_str = dia["saldo_dia"].lstrip("-")
                horas, minutos, segundos = map(int, saldo_str.split(":"))
                saldo_diario = timedelta(hours=horas, minutes=minutos, seconds=segundos)

                if negativo:
                    saldo_diario = -saldo_diario

                saldo_dia_total += saldo_diario

            if dia["tipo"] == FALTA:
                qtd_faltas += 1

        except ValueError as e:
            log.error(f"Erro ao converter saldo do dia: {e}")

    return qtd_faltas, saldo_dia_total


def dividir_intervalo_datas(dados):
    """
    Divide o intervalo de datas em dois objetos se o período cruzar meses diferentes.
    Args:
        dados (dict): dados que serão usados na criação dos objetos.
    Returns:
        list: Lista de objetos (dicionários) com as datas ajustadas.
    """
    objetos = []

    dt_inicio = datetime.strptime(dados["data_inicio"], "%Y-%m-%d").date()
    dt_fim = datetime.strptime(dados["data_fim"], "%Y-%m-%d").date()

    if dt_inicio.month == dt_fim.month and dt_inicio.year == dt_fim.year:
        objetos.append({**dados})
    else:
        del dados["data_inicio"], dados["data_fim"]
        ultimo_dia_mes_inicio = monthrange(dt_inicio.year, dt_inicio.month)[1]
        data_fim_mes_inicio = datetime(
            dt_inicio.year, dt_inicio.month, ultimo_dia_mes_inicio
        )

        objetos.append(
            {
                "data_inicio": dt_inicio.strftime("%Y-%m-%d"),
                "data_fim": data_fim_mes_inicio.strftime("%Y-%m-%d"),
                **dados,
            }
        )

        data_inicio_mes_seguinte = data_fim_mes_inicio + timedelta(days=1)
        objetos.append(
            {
                "data_inicio": data_inicio_mes_seguinte.strftime("%Y-%m-%d"),
                "data_fim": dt_fim.strftime("%Y-%m-%d"),
                **dados,
            }
        )

    return objetos


def get_data_inicio_fim_ponto(servidor, inicio, fim):
    if servidor.data_exercicio > inicio:
        inicio = servidor.data_exercicio

    if servidor.data_exercicio > fim:
        fim = servidor.data_exercicio

    return inicio, fim
