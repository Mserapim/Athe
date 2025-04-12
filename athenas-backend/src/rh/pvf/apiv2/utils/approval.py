from rh.pvf.const import *
from django.db.models import Q

# Funções base para os filtros da tela de aprovações do vida funcional


def group_list(employee):
    """Retorna uma lista dos steps relacionados aos grupos de aprovação VDF"""
    groups = get_employee_approver(employee)
    groups_list = []
    for group in groups:
        groups_list.append(REQUEST_STEP_GROUP.get(group, 0))

    return groups_list


def get_employee_approver(employee):
    """Retorna o(s) grupo(s) em que o servidor está vinculado"""
    groups = {}
    for group in employee.user.groups.all():
        groups[group.name] = group.name

    return groups


def belongs_group(employee):
    """Verifica se o servidor pertence ao determinado grupo de acesso geral"""
    groups = get_employee_approver(employee)
    belongs = []
    for group in groups:
        if group in [GROUPS_PVF["GS"], GROUPS_PVF["GM"]]:
            belongs.append(group)
        if group in [GROUPS_PVF["COGER"], GROUPS_PVF["ASS_COGER"]]:
            belongs.append(group)
    return belongs


def belongs_group_dgp(employee):
    """Verifica se o servidor pertence ao grupo Gerência de Membros ou Servidores"""
    groups = belongs_group(employee)
    if GROUPS_PVF["GM"] in groups:
        return GROUPS_PVF["GM"]
    if GROUPS_PVF["GS"] in groups:
        return GROUPS_PVF["GS"]
    return ""


def group_list_all():
    """Retorna uma lista de todos eteps VDF"""
    groups_list = []
    for group in REQUEST_STEP:
        groups_list.append(REQUEST_STEP.get(group, 0))
    return groups_list


def approver_button_request(request, employee):
    """Retorna se o servidor é aprovador do step atual"""
    if (
        request.step_current in group_list(employee)
        or request.approver == employee
        or employee.pk in get_substitutes_approver(request)
    ):
        return True
    else:
        return False


def get_substitutes_approver(request):
    """Retorna lista com os 'pks' dos servidores 'substitutos'"""

    if not request.has_substitute:
        return []
    science_ids = request.portalrequesthistory_set.filter(
        action=REQUEST_ACT_SCIENCE
    ).values_list("user__servidor__pk", flat=True)
    science_ids = list(science_ids)

    pr_substitute = request.portal_request_substitute.exclude(
        substitute__pk__in=set(science_ids)
    )
    if pr_substitute:
        return list(pr_substitute.values_list("substitute__pk", flat=True))
    else:
        return []


def filtro_tipo_servidor(employee):
    groups = get_employee_approver(employee)
    if GROUPS_PVF["GM"] in groups:
        return ["MBR", "MEL", "MEC"]
    elif GROUPS_PVF["COGER"] in groups:
        return ["MBR", "MEL", "MEC"]
    elif GROUPS_PVF["ASS_COGER"] in groups:
        return ["MBR", "MEL", "MEC"]
    elif GROUPS_PVF["GS"] in groups:
        return [
            "EFE",
            "CMS",
            "ECM",
            "RCM",
            "RFC",
            "EFC",
            "REQ",
            "VOL",
            "EXT",
            "EST",
            "RES",
        ]


def query_aprovador_coger(servidor):
    """
    Retorna uma query que filtra as solicitações onde o servidor, coger e assessoria da coger
    são os aprovadores ou podem consultar a solicitação
    Args:
        servidor: O objeto de servidor que está logado.
    Returns:
        Queryset: query da consulta

    """
    return Q(
        Q(approver__pk=servidor.pk)
        | Q(portal_request_substitute__substitute__pk=servidor.pk)
        | Q(
            step_current__in=[
                REQUEST_STEP_CORREGEDORIES_ADVISORY,
                REQUEST_STEP_CORREGEDORATION,
                REQUEST_STEP_PGJ,
            ]
        )
        | Q(status__in=[STS_WAI_SUBS_SCIENCE])
        | Q(portalrequesthistory__group__in=list(get_employee_approver(servidor)))
        | Q(portalrequesthistory__user=servidor.user)
        & Q(
            portalrequesthistory__action__in=[
                REQUEST_ACT_DEFER,
                REQUEST_ACT_INDEFER,
                REQUEST_ACT_SCIENCE,
                REQUEST_ACT_ANNOTATION,
                REQUEST_ACT_EFFECTIVENESS,
            ]
        )
    )


def query_aprovador(servidor):
    """
    Retorna uma query que filtra as solicitações onde o servidor é aprovador
    ou podem consultar a solicitação
    Args:
        servidor: O objeto de servidor que está logado.
    Returns:
        Queryset: query da consulta

    """
    return Q(
        Q(approver__pk=servidor.pk)
        | Q(portal_request_substitute__substitute__pk=servidor.pk)
        | Q(step_current__in=group_list(servidor))
        | Q(portalrequesthistory__group__in=list(get_employee_approver(servidor)))
        | Q(portalrequesthistory__user=servidor.user)
        & Q(
            portalrequesthistory__action__in=[
                REQUEST_ACT_DEFER,
                REQUEST_ACT_INDEFER,
                REQUEST_ACT_SCIENCE,
                REQUEST_ACT_ANNOTATION,
                REQUEST_ACT_EFFECTIVENESS,
            ]
        )
    )


def query_relatorio_semestral():
    """
    Retorna uma query que filtra as solicitações de relatório
    semestral do teletrabalho

    Returns:
        Queryset: query da consulta

    """
    return Q(request_type=REQUEST_TYPE_RELATORIO_TELE_SEMESTRAL)


def query_teletrabalho():
    """
    Retorna uma query que filtra as solicitações de teletrabalho, relatorio semestral
    e cancelamento do teletrabalho
    Returns:
        Queryset: query da consulta

    """
    return Q(
        request_type__in=[
            REQUEST_TYPE_RELATORIO_TELE_SEMESTRAL,
            REQUEST_TYPE_CANCELAMENTO_TELETRABALHO,
            REQUEST_TYPE_TELEWORK,
        ]
    )


def query_venda_plantoes_pgj():
    """
    Retorna uma query que filtra as solicitações de venda de plantões
    Returns:
        Queryset: query da consulta

    """
    return Q(
        status=STS_EFETIVACAO_AUTOMATICA,
        employee__type_by_possession__in=["MBR", "MEL", "MEC"],
    )


def query_approvals(query, employee):
    """Realizar a consulta e retornar uma query com as solicitação de pendentes de aprovação do servidor"""
    from rh.pvf.apiv2.utils.base import expressao_query

    belongs_gp = belongs_group(employee)
    grupos_approver = get_employee_approver(employee)

    if (
        GROUP_SERVER in belongs_gp
        or GROUP_MEMBER in belongs_gp
        or GROUP_AUDIT in belongs_gp
    ):
        return query.distinct()

    filtro = []
    if GROUP_ASS_COGER in belongs_gp or GROUP_COGER in belongs_gp:
        filtro.append(query_aprovador_coger(employee))
    if not belongs_gp:
        filtro.append(query_aprovador(employee))
    if GROUPO_RELATORIO_SEMESTRAL in grupos_approver:
        filtro.append(query_relatorio_semestral())
    if GROUPO_TELETRABALHO in grupos_approver or GROUP_GER_DEV in grupos_approver:
        filtro.append(query_teletrabalho())
    if GROUP_PGJ in grupos_approver:
        filtro.append(query_venda_plantoes_pgj())

    filtro = expressao_query(filtro)
    return query.filter(filtro).distinct()


def acoes_aprovador(solicitacao, servidor):
    """
    Processa e retorna as ações permitidas para solicitação.
    Args:
        request: O objeto de solicitação recebida.
        employee: O objeto de servidor que está logado.
    Returns:
        list[]: lista das ações permitidas para solicitação

    """

    from rh.pvf.acoesvdf import (
        BaseAcao,
        AcoesAfastamento,
        AcoesFolhaPonto,
        AcoesPlantao,
        AcoesExercicioCumulativo,
        AcoesTeletrabalho,
        AcoesProgressaoH,
        AcoesProgressaoV,
        AcoesSolicitacaoAuxCrecheDepenIR,
        AcoesDesbloqueioTeletrabalho,
        AcoesCreditoDispensaEleitoral,
        AcoesVendaPlantoes,
    )

    if solicitacao.request_type == REQUEST_TYPE_ABSENCE:
        return AcoesAfastamento.retorna_acoes_solicitacao(solicitacao, servidor)
    elif solicitacao.request_type == REQUEST_TYPE_POINT_SHEET:
        return AcoesFolhaPonto.retorna_acoes_solicitacao(solicitacao, servidor)
    elif solicitacao.request_type == REQUEST_TYPE_SERVER_DUTY:
        return AcoesPlantao.retorna_acoes_solicitacao(solicitacao, servidor)
    elif solicitacao.request_type == REQUEST_TYPE_CUMULATIVE_EXERCISE:
        return AcoesExercicioCumulativo.retorna_acoes_solicitacao(solicitacao, servidor)
    elif solicitacao.request_type == REQUEST_TYPE_TELEWORK:
        return AcoesTeletrabalho.retorna_acoes_solicitacao(solicitacao, servidor)
    elif solicitacao.request_type == REQUEST_TYPE_PROGRESSION_H:
        return AcoesProgressaoH.retorna_acoes_solicitacao(solicitacao, servidor)
    elif solicitacao.request_type == REQUEST_TYPE_PROGRESSION_V:
        return AcoesProgressaoV.retorna_acoes_solicitacao(solicitacao, servidor)
    elif solicitacao.status == STS_EFETIVACAO_AUTOMATICA:
        return AcoesVendaPlantoes.retorna_acoes_solicitacao(solicitacao, servidor)
    elif solicitacao.request_type == REQUEST_TYPE_SOLICITACAO_AUX_CRECHE_DEPEN_IR:
        return AcoesSolicitacaoAuxCrecheDepenIR.retorna_acoes_solicitacao(
            solicitacao, servidor
        )
    elif solicitacao.request_type == REQUEST_TYPE_DESBLOQUEIO_TELETRABALHO:
        return AcoesDesbloqueioTeletrabalho.retorna_acoes_solicitacao(
            solicitacao, servidor
        )
    elif solicitacao.request_type == REQUEST_TYPE_CREDITO_DISPENSA_ELEITORAL:
        return AcoesCreditoDispensaEleitoral.retorna_acoes_solicitacao(
            solicitacao, servidor
        )
    else:
        return BaseAcao.retorna_acoes_solicitacao(solicitacao, servidor)
