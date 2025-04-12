import calendar
from datetime import datetime
from django.db.models import Q, Min, Max
import json
from rh.afastamento.models import BaseLicencaAfastamento
from rh.const import CANCELADO
from rh.models import Servidor
from common.util.send_email import EmailNotification
from rh.pvf.const import (
    STS_CANCELED_APPLICANT,
    STS_STAND_BY,
    STS_CANCELED_DGP,
    STS_REJECTED,
)
from standard.models import EmailTemplate, Item
from contrib.utils import getLogger
from django.template.loader import render_to_string


log = getLogger(__name__)


def proxima_referencia(mes, ano):
    """
    Função que retorna a proxima referencia
    Args:
        mes_referencia: int
        ano_referencia: int
    Returns:
        tupla:(mes, ano)
    """
    ref_mes = 1 if mes == 12 else mes + 1
    ref_ano = ano + 1 if mes == 12 else ano
    return ref_mes, ref_ano


def referencia_anterior(mes, ano):
    """
    Função que retorna referencia anterior
    Args:
        mes: int
        ano: int
    Returns:
        tupla:(mes, ano)
    """
    ref_mes = 12 if mes == 1 else mes - 1
    ref_ano = ano - 1 if mes == 1 else ano
    return ref_mes, ref_ano


def data_inicio_fim_referencia(mes, ano):
    """
    Função que retorna as datas inicial e final de uma referencia
    Args:
        mes_referencia: int
        ano_referencia: int
    Returns:
        tupla:(data_inicio, data_fim)
    """
    dt_inicio_ref = datetime(ano, mes, 1).date()
    dt_fim_ref = datetime(ano, mes, calendar.monthrange(ano, mes)[1]).date()
    return dt_inicio_ref, dt_fim_ref


def get_aprovador_vdf(servidor):
    """
    Função que busca o aprovador VDF
    Args:
        servidor: objeto
    Returns:
        aprovador: objeto
    """
    from rh.pvf.models import PortalRequest

    aprovador = None
    try:
        instancia_solicitacao = PortalRequest()
        aprovador = instancia_solicitacao.get_immediate_boss(servidor)
    except:
        log.error("Aprovador não encontrado.")
        pass
    return aprovador


def agrupar_aprovador_folha_ponto(servidor, dict_aprovadores):
    """
    Função que agrupar os suborninados por aprovador
    Args:
        servidor: objeto
        dict_aprovadores: dict
    """
    from rh.pvf.models import SendingTimeSheet

    aprovador = get_aprovador_vdf(servidor)
    if aprovador:
        status_excluidos = [
            STS_CANCELED_APPLICANT,
            STS_STAND_BY,
            STS_CANCELED_DGP,
            STS_REJECTED,
        ]
        ultimo_envio = (
            SendingTimeSheet.objects.filter(employee=servidor)
            .exclude(status__in=status_excluidos)
            .last()
        )
        cargo_quadro = str(getattr(servidor.job_position(), "cargo", ""))
        ultimo_envio = (
            f"{ultimo_envio.reference_month:02d}/{ultimo_envio.reference_year}"
            if ultimo_envio
            else None
        )

        dict_aprovadores.setdefault(aprovador.pk, []).append(
            f"{servidor.__str__()} - {cargo_quadro or ''} - Último envio({ultimo_envio or ''})"
        )


def filtro_gestor_folha_ponto(params):
    periodo_ano = int(params.get("ano_competencia", datetime.today().year))
    periodo_mes = int(params.get("mes_competencia", datetime.today().month))

    filtro_email = params.get("filtro_email", False)

    filtro_notificado = params.get("notificado", None)
    teletrabalho = params.get("teletrabalho", "teletrabalho_nao")

    primeiro_dia_mes = datetime(periodo_ano, periodo_mes, 1)
    ultimo_dia_mes = datetime(
        periodo_ano, periodo_mes, calendar.monthrange(periodo_ano, periodo_mes)[1]
    )

    posses_default = [
        "EFE",
        "ECM",
        "EFC",
        "CMS",
        "REQ",
        "REX",
        "RCM",
        "RFC",
        "RES",
        "EST",
        "VOL",
        "EXT",
    ]
    filtro_tipo_posse = (
        json.loads(params["posses"]) if params["posses"] else posses_default
    )

    query = Servidor.objects.filter(
        Q(
            movimentacaopessoal__movimentacaoposse__data_desligamento__gt=primeiro_dia_mes
        )
        | Q(movimentacaopessoal__movimentacaoposse__data_desligamento__isnull=True),
        Q(movimentacaopessoal__movimentacaoposse__isnull=False),
        Q(movimentacaopessoal__movimentacaoposse__data_posse__lte=ultimo_dia_mes),
        Q(type_by_possession__in=filtro_tipo_posse),
    ).distinct()

    if teletrabalho == "teletrabalho_sim":
        query = query.filter(
            Q(
                movimentacaopessoal__movimentacaoteletrabalho__data_inicio__lte=ultimo_dia_mes
            ),
            Q(
                movimentacaopessoal__movimentacaoteletrabalho__data_fim__gte=ultimo_dia_mes
            ),
        )
    else:
        query = query.exclude(
            Q(
                movimentacaopessoal__movimentacaoteletrabalho__data_inicio__lte=ultimo_dia_mes
            ),
            Q(
                movimentacaopessoal__movimentacaoteletrabalho__data_fim__gte=ultimo_dia_mes
            ),
        )

    filtro_status = params.get("status", "todos")

    if filtro_notificado:
        if filtro_notificado == "sim":
            query = query.filter(
                folha_ponto_historico_notificacoes__referencia_ano=periodo_ano,
                folha_ponto_historico_notificacoes__referencia_mes=periodo_mes,
            )
        elif filtro_notificado == "nao":
            query = query.exclude(
                folha_ponto_historico_notificacoes__referencia_ano=periodo_ano,
                folha_ponto_historico_notificacoes__referencia_mes=periodo_mes,
            )

    query_isento = query.filter(
        Q(
            Q(movimentacaopessoal__baselicencaafastamento__data_fim__gte=ultimo_dia_mes)
            & Q(
                movimentacaopessoal__baselicencaafastamento__data_inicio__lte=primeiro_dia_mes
            )
        ),
        Q(movimentacaopessoal__baselicencaafastamento__estado__in=[1, 2, 3]),
    )

    if filtro_status:
        if filtro_status == "nao_criado":
            status_possiveis = [2, 3, 4]

            query_status = query.filter(
                Q(
                    portal_request_employee__sendingtimesheet__reference_year=periodo_ano,
                    portal_request_employee__sendingtimesheet__reference_month=periodo_mes,
                    portal_request_employee__status__in=status_possiveis,
                )
            ).values_list("pk", flat=True)

            query = query.exclude(
                pk__in=query_isento.values_list("pk", flat=True)
            ).exclude(pk__in=query_status)

        elif filtro_status == "aguardando_aprovador":
            query = query.filter(
                Q(portal_request_employee__status=2),
                Q(
                    portal_request_employee__sendingtimesheet__reference_year=periodo_ano
                ),
                Q(
                    portal_request_employee__sendingtimesheet__reference_month=periodo_mes
                ),
            )
        elif filtro_status == "aguardando_efetivacao":
            query = query.filter(
                Q(portal_request_employee__status=3),
                Q(
                    portal_request_employee__sendingtimesheet__reference_year=periodo_ano
                ),
                Q(
                    portal_request_employee__sendingtimesheet__reference_month=periodo_mes
                ),
            )
        elif not filtro_email and filtro_status == "efetivado":
            query = query.filter(
                Q(portal_request_employee__status=4),
                Q(
                    portal_request_employee__sendingtimesheet__reference_year=periodo_ano
                ),
                Q(
                    portal_request_employee__sendingtimesheet__reference_month=periodo_mes
                ),
            )
        elif filtro_email and filtro_status == "todos":
            query_efetivado = query.filter(
                Q(portal_request_employee__status=4),
                Q(
                    portal_request_employee__sendingtimesheet__reference_year=periodo_ano
                ),
                Q(
                    portal_request_employee__sendingtimesheet__reference_month=periodo_mes
                ),
            ).values_list("pk", flat=True)

            query = query.exclude(pk__in=query_efetivado).exclude(
                pk__in=query_isento.values_list("pk", flat=True)
            )

        elif not filtro_email and filtro_status == "isento":
            query = query_isento
        elif filtro_email:
            query = query.none()

    return query.distinct()


def enviar_email_gestor_folha_ponto(params):
    """
    Função que envia notificação de email do folha ponto
    Args:
       params: dict
       {mes_competencia,ano_competencia,servidor,aprovador}
    """

    competencia = f"{params['mes_competencia']}/{params['ano_competencia']}"
    servidor = params["servidor"]

    if servidor.type_by_possession == "EST":
        codigo_email = "ENTREGA_FOLHA_PONTO_NOTIFICACAO_ESTAGIARIO"
    elif servidor.type_by_possession == "RES":
        codigo_email = "ENTREGA_FOLHA_PONTO_NOTIFICACAO_RESIDENTE"
    else:
        codigo_email = "ENTREGA_FOLHA_PONTO_NOTIFICACAO"

    email_template = EmailTemplate.objects.get(code=codigo_email)

    ultimo_envio = params["ultimo_envio"]

    if ultimo_envio:
        ultimo_envio = (
            f"{ultimo_envio.reference_month:02d}/{ultimo_envio.reference_year}"
        )

    conteudo = (
        email_template.contents.replace(
            "@nome_servidor%", servidor.pessoa_fisica.social_name
        )
        .replace("@comp%", competencia)
        .replace("@comp_ultimo_envio%", ultimo_envio if ultimo_envio else "")
    )

    lista_destinatarios = [
        {
            "email": servidor.pessoa_fisica.email_institucional,
            "nome": servidor.pessoa_fisica.social_name,
            "idUsuario": servidor.id_usuario_mastiff,
        }
    ]

    config_email_item = Item.objects.get(key="notificacao_envio_folha_ponto")

    lista_email = config_email_item.value.split(",")

    for email in lista_email:
        lista_destinatarios.append({"email": email, "nome": email.upper()})
    html_content = render_to_string("util/template_email.html", {"message": conteudo})
    EmailNotification().send_email_default(
        lista_destinatarios, email_template.subject, html_content
    )


def enviar_email_gestor_folha_ponto_aprovador(params):
    """
    Função que envia notificação de email do folha ponto de aprovador
    Args:
       params: dict
       {mes_competencia,ano_competencia,aprovador, conteudo}
    """

    competencia = f"{params['mes_competencia']}/{params['ano_competencia']}"
    aprovador = params["aprovador"]
    conteudo = params["conteudo"]

    codigo_email = "ENTREGA_FOLHA_PONTO_NOTIFICACAO_GESTOR"
    email_template = EmailTemplate.objects.get(code=codigo_email)
    lista_html = (
        "<ul>\n" + "\n".join(f"  <li>{item}</li>" for item in conteudo) + "\n</ul>"
    )

    conteudo = (
        email_template.contents.replace(
            "%nome_servidor%", aprovador.pessoa_fisica.social_name
        )
        .replace("%mes%", competencia)
        .replace("%conteudo%", lista_html)
    )

    lista_destinatarios = [
        {
            "email": aprovador.pessoa_fisica.email_institucional,
            "nome": aprovador.pessoa_fisica.social_name,
            "idUsuario": aprovador.id_usuario_mastiff,
        }
    ]

    html_content = render_to_string("util/template_email.html", {"message": conteudo})
    EmailNotification().send_email_default(
        lista_destinatarios, email_template.subject, html_content
    )


def get_ultimo_dia_referencia(ano, mes):
    return datetime(ano, mes, calendar.monthrange(ano, mes)[1]).date()
