from datetime import datetime

from django.db.models import Q, F, OuterRef, Case, When, Value, Subquery, CharField
from django.db.models.functions import Concat, Cast

from contrib.utils import remove_html_tags
from standard.models import Choice
from rh.models import Servidor
from rh.pvf.const import *
from rh.pvf.models import PortalRequestHistory, PortalRequest
from rh.dayoff.models import Activity
from contrib.utils import getLogger, remover_caracteres_invalidos


log = getLogger(__name__)


def get_data_report(params):
    portal_request_histories = (
        PortalRequestHistory.objects.filter(**get_filters(params))
        .annotate(**get_annotation())
        .values(
            "codigo_vdf",
            "servidor",
            "tipo_solicitacao",
            "aprovador_atual",
            "situacao",
            "mes_referencia",
            "dias_aguardando_aprovacao",
            "observacao",
            "data_acao",
            "acao",
            "grupo",
            "solicitante",
            "periodo",
            "periodo_ano",
            "periodo_titulo",
        )
    )
    if params.get("keyword"):
        portal_request_histories = portal_request_histories.filter(
            get_keyword_filter(params.get("keyword"))
        )
    portal_request_histories = portal_request_histories.order_by(
        "-portal_request_id"
    ).distinct()
    tipo_solicitacao = Choice.objects.get_options("pvf", "REQUEST_TYPE_VDF")
    situacao = Choice.objects.get_options("pvf", "REQUEST_STATUS")
    tipo_acao = Choice.objects.get_options("pvf", "ACTION_TAKEN")
    portal_request_histories = list(portal_request_histories)
    for requests in portal_request_histories:
        titulo = requests.get("periodo_titulo")
        ano = requests.get("periodo_ano")
        periodo = requests.get("periodo")
        data_acao = requests.get("data_acao").strftime("%d/%m/%Y")
        dias_aguardando_aprovacao = requests.get("dias_aguardando_aprovacao")
        if requests.get("situacao") in [
            STS_EFFECTIVE,
            STS_REJECTED,
            STS_CANCELED_DGP,
            STS_CANCELED_APPLICANT,
        ]:
            requests["dias_aguardando_aprovacao"] = 0
        else:
            requests["dias_aguardando_aprovacao"] = abs(
                (dias_aguardando_aprovacao - datetime.today().date()).days
            )
        requests["grupo"] = get_group_name(requests.get("grupo", ""))
        requests["tipo_solicitacao"] = get_label(
            str(requests.get("tipo_solicitacao")), tipo_solicitacao
        )
        requests["situacao"] = get_label(str(requests.get("situacao")), situacao)
        requests["acao"] = get_label(str(requests.get("acao")), tipo_acao)
        requests["data_acao"] = data_acao
        if requests.get("observacao"):
            observacao = remove_html_tags(requests.get("observacao"))
            requests["observacao"] = remover_caracteres_invalidos(observacao)
        else:
            requests["observacao"] = ""
        if not titulo and not ano and not periodo:
            requests["periodo_grupo"] = ""
            requests.pop("periodo_titulo")
            requests.pop("periodo_ano")
            requests.pop("periodo")
        else:
            requests["periodo_grupo"] = (
                f"{titulo} - {ano} / {periodo}" if ano else f"{titulo} - {periodo}"
            )
            requests.pop("periodo_titulo")
            requests.pop("periodo_ano")
            requests.pop("periodo")
    keys = {
        "codigo_vdf": "CÓDIGO VDF",
        "servidor": "SERVIDOR",
        "tipo_solicitacao": "TIPO SOLICITACAO",
        "aprovador_atual": "APROVADOR ATUAL",
        "situacao": "SITUAÇÃO",
        "mes_referencia": "MÊS REFERÊNCIA",
        "dias_aguardando_aprovacao": "DIAS AGUARDANDO APROVAÇÃO",
        "observacao": "OBSERVAÇÃO",
        "data_acao": "DATA AÇÃO",
        "acao": "AÇÃO",
        "grupo": "GRUPO",
        "solicitante": "SOLICITANTE",
        "periodo_grupo": "PERIODO GRUPO",
    }
    return {
        "title": params.get("report_name", ""),
        "data": portal_request_histories,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "keys": keys,
    }


def get_label(campo, opcoes):
    for item in opcoes:
        if campo == item.get("cvalue"):
            return item.get("label")
    return campo


def get_group_name(group):
    if group:
        if group in [GROUPS_PVF["GS"], GROUPS_PVF["GM"]]:
            return "DGP"
        elif group in [GROUPS_PVF["ASS_JUR_1"]]:
            return "ASSJUR1"
        elif group in [GROUPS_PVF["PROG_DG"]]:
            return "PROG_DG"
        elif group in [GROUPS_PVF["ASS_JUR_2"]]:
            return "ASSJUR2"
        elif group == GROUP_SUB_ADM:
            return "SUB ADMINISTRATIVA"
        else:
            group_name = group.split("-").pop().upper()
            return group_name
    return ""


def get_annotation():
    aprovador_atual = Case(
        When(
            Q(
                portal_request__approver__isnull=True,
                portal_request__step_current=REQUEST_STEP_APPROVER,
            ),
            then=Value(""),
        ),
        When(
            portal_request__approver__isnull=False,
            then=F("portal_request__approver__pessoa_fisica__nome"),
        ),
        When(portal_request__status=STS_EFFECTIVE, then=Value("")),
        default=Cast(F("portal_request__step_current"), output_field=CharField()),
        output_field=CharField(),
    )

    portal_requests = PortalRequest.objects.filter(id=OuterRef("portal_request"))
    dias_aguardando_aprovacao = Subquery(
        portal_requests.order_by("-date").values("date")[:1]
    )
    activities = Activity.objects.filter(
        activity_requests=OuterRef("portal_request__portalrequestusufruct")
    )

    periodo_ano = Case(
        When(
            Q(
                portal_request__request_type__in=[
                    REQUEST_TYPE_SCHEDULE,
                    REQUEST_TYPE_RETIFICATION,
                ],
                portal_request__portalrequestusufruct__activity__isnull=False,
            ),
            then=Subquery(
                activities.values("acquisition_period__group_period__year_reference")[
                    :1
                ]
            ),
        ),
    )
    periodo_titulo = Case(
        When(
            Q(
                portal_request__request_type__in=[
                    REQUEST_TYPE_SCHEDULE,
                    REQUEST_TYPE_RETIFICATION,
                ],
                portal_request__portalrequestusufruct__activity__isnull=False,
            ),
            then=Subquery(
                activities.values("acquisition_period__group_period__title")[:1]
            ),
        ),
    )
    periodo = Case(
        When(
            Q(
                portal_request__request_type__in=[
                    REQUEST_TYPE_SCHEDULE,
                    REQUEST_TYPE_RETIFICATION,
                ],
                portal_request__portalrequestusufruct__activity__isnull=False,
            ),
            then=Subquery(
                activities.values("acquisition_period__group_period__period")[:1]
            ),
        ),
    )

    mes_referencia = Case(
        When(
            portal_request__sendingtimesheet__isnull=False,
            then=Concat(
                Cast(
                    Subquery(
                        portal_requests.values("sendingtimesheet__reference_month")[:1]
                    ),
                    output_field=CharField(),
                ),
                Value("/"),
                Cast(
                    Subquery(
                        portal_requests.values("sendingtimesheet__reference_year")[:1]
                    ),
                    output_field=CharField(),
                ),
            ),
        ),
        When(
            portal_request__sendingtelework__isnull=False,
            then=Concat(
                Cast(
                    Subquery(
                        portal_requests.values("sendingtelework__reference_month")[:1]
                    ),
                    output_field=CharField(),
                ),
                Value("/"),
                Cast(
                    Subquery(
                        portal_requests.values("sendingtelework__reference_year")[:1]
                    ),
                    output_field=CharField(),
                ),
            ),
        ),
        When(
            portal_request__pvfsolicitacaodesbloqueioteletrabalho__isnull=False,
            then=Concat(
                Cast(
                    Subquery(
                        portal_requests.values(
                            "pvfsolicitacaodesbloqueioteletrabalho__referencia_mes"
                        )[:1]
                    ),
                    output_field=CharField(),
                ),
                Value("/"),
                Cast(
                    Subquery(
                        portal_requests.values(
                            "pvfsolicitacaodesbloqueioteletrabalho__referencia_ano"
                        )[:1]
                    ),
                    output_field=CharField(),
                ),
            ),
        ),
        default=Value(""),
    )

    annotate = {
        "codigo_vdf": F("portal_request_id"),
        "servidor": Concat(
            Cast(F("user__servidor__matricula"), output_field=CharField()),
            Value(": "),
            F("user__servidor__pessoa_fisica__nome"),
        ),
        "tipo_solicitacao": F("portal_request__request_type"),
        "aprovador_atual": aprovador_atual,
        "situacao": F("portal_request__status"),
        "dias_aguardando_aprovacao": dias_aguardando_aprovacao,
        "periodo_ano": periodo_ano,
        "periodo_titulo": periodo_titulo,
        "periodo": periodo,
        "mes_referencia": mes_referencia,
        "observacao": F("observation"),
        "data_acao": F("date"),
        "acao": F("action"),
        "grupo": F("group"),
        "solicitante": Concat(
            Cast(F("portal_request__employee__matricula"), output_field=CharField()),
            Value(": "),
            F("portal_request__employee__pessoa_fisica__nome"),
        ),
        "matricula": Cast(
            F("portal_request__employee__matricula"), output_field=CharField()
        ),
        "identificacao": Cast(F("codigo_vdf"), output_field=CharField()),
    }
    return annotate


def get_filters(params):
    filters = {}
    if params.get("usuarios[]") and params.get("filtrar_por") == "solicitacao":
        filters["employee__id__in"] = params.get("usuarios[]")
    elif params.get("usuarios[]") and params.get("filtrar_por") == "acao":
        usuarios = Servidor.objects.filter(id__in=params.get("usuarios[]")).values_list(
            "user_id", flat=True
        )
        filters["user_id__in"] = usuarios
    if params.get("tipos_solicitacoes[]"):
        filters["portal_request__portal_request_type__in"] = params.get(
            "tipos_solicitacoes[]"
        )
    if params.get("situacoes[]"):
        filters["portal_request__status__in"] = params.get("situacoes[]")
    if params.get("categorias[]"):
        type_by_possessions = []
        for employee_type in params.get("categorias[]"):
            if employee_type == "SERVIDOR":
                type_by_possessions.extend(
                    ["EFE", "CMS", "ECM", "RCM", "RFC", "EFC", "REQ", "VOL", "EXT"]
                )
            elif employee_type == "MEMBRO":
                type_by_possessions.extend(["MBR", "MEL", "MEC"])
            elif employee_type == "ESTAGIARIO":
                type_by_possessions.extend(["EST"])
            elif employee_type == "RESIDENTE":
                type_by_possessions.extend(["RES"])
        filters["portal_request__employee__type_by_possession__in"] = (
            type_by_possessions
        )
    if params.get("tipos_acoes[]"):
        filters["action__in"] = params.get("tipos_acoes[]")
    if params.get("solicitacao_inicio_em") or params.get("solicitacao_fim_em"):
        filters = {
            **filters,
            **filtrar_data(
                "portal_request__date",
                params.get("solicitacao_inicio_em"),
                params.get("solicitacao_fim_em"),
            ),
        }
    if params.get("acao_inicio_em") or params.get("acao_fim_em"):
        filters = {
            **filters,
            **filtrar_data(
                "date", params.get("acao_inicio_em"), params.get("acao_fim_em")
            ),
        }
    return filters


def get_keyword_filter(keyword):
    keyword_filters = {
        "solicitante__icontains": keyword,
        "identificacao__icontains": keyword,
        "matricula__icontains": keyword,
    }
    return Q(**keyword_filters, _connector=Q.OR)


def filtrar_data(campo, antes, depois):
    filtro = {}
    if antes and depois:
        filtro.update({f"{campo}__range": [antes, depois]})
    elif antes:
        filtro.update({f"{campo}__lte": antes})
    elif depois:
        filtro.update({f"{campo}__gte": depois})
    return filtro
