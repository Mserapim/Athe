import base64
from datetime import datetime

from django.db.models import (
    Count,
    Value,
    Q,
    F,
    ExpressionWrapper,
    IntegerField,
    OuterRef,
    Exists,
    CharField,
    Case,
    When,
    Subquery,
)
from django.db.models.functions import (
    Coalesce,
    LPad,
    ExtractDay,
    ExtractMonth,
    ExtractYear,
    Concat,
    Cast,
)

from contrib.utils import getLogger
from rh.models import (
    CargoQuadro,
    Servidor,
    MovimentacaoTeletrabalho,
    MovimentacaoPosse,
    ServidorLotacao,
    MovimentacaoPessoal,
    Cargo,
)
from standard.models import Choice

log = getLogger(__name__)


def get_data_report(params):
    report_keys = [
        "cargo_nome",
        "existentes",
        "membro",
        "servidor",
        "efetivo_em_comissao",
        "comissionado",
        "sem_vinculo",
        "vagos",
        "pedidos_nomeacao",
        "pedidos_exoneracao",
        "saldo",
    ]

    cargos = CargoQuadro.objects.annotate(**get_sintetico_annotation()).values(
        "cargo_nome",
        "existentes",
        "membro",
        "servidor",
        "efetivo_em_comissao",
        "comissionado",
        "sem_vinculo",
        "vagos",
        "pedidos_nomeacao",
        "pedidos_exoneracao",
        "saldo",
    )

    if (
        params.get("cargos")
        and len(params.get("cargos")) > 0
        and params.get("cargos")[0] != ""
    ):
        cargos = cargos.filter(cargo__id__in=params.get("cargos"))

    if params.get("keyword"):
        cargos = cargos.filter(cargo__nome__icontains=params.get("keyword"))

    if params.get("filtros"):
        values = params.get("filtros")[0].get("value")
        cargos = cargos.filter(cargo__tipo_lei_cargo__in=values)

    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    return {
        "data": cargos,
        "title": "CONSULTA CARGOS VAGOS E OCUPADOS",
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
        "keys": report_keys,
        "user": params.get("user"),
    }


def get_analitico_data(params):
    report_keys = [
        "SERVIDOR_ID",
        "matricula",
        "servidor_ativo",
        "servidor_nome",
        "tipo_posse",
        "cargo",
        "lotacao",
        "data_de_inicio",
        "teletrabalho",
        "data_inicio_provimento",
        "data_fim_provimento",
    ]

    teletrabalho_exists = Exists(
        MovimentacaoTeletrabalho.objects.filter(
            servidor=OuterRef("servidor__id"), ativo=True
        )
    )

    tipo_posse = Choice.objects.filter(
        app_label="rh", name="CLASSIF_EMPLOYEE_BY_POSSESSION", active=True
    ).values("cvalue", "label")
    data_de_inicio = formatar_data_por_query("data_exercicio")
    data_inicio_provimento = formatar_data_por_query("data_posse")
    data_fim_provimento = formatar_data_por_query("data_desligamento")

    annotation = {
        "SERVIDOR_ID": F("servidor__id"),
        "matricula": F("servidor__matricula"),
        "servidor_ativo": Case(
            When(servidor__ativo=True, then=Value("SIM")),
            default=Value("NÃO"),
            output_field=CharField(),
        ),
        "servidor_nome": F("servidor__pessoa_fisica__nome"),
        "tipo_posse": F("servidor__type_by_possession"),
        "cargo": F("quadro__cargo__nome"),
        "lotacao": Subquery(
            ServidorLotacao.objects.filter(
                movimentacao_posse=OuterRef("id"),
                designacao=False,
                ativo=True,
            )
            .order_by("-id")
            .values("lotacao__nome")[:1]
        ),
        "data_de_inicio": data_de_inicio,
        "teletrabalho_exists": teletrabalho_exists,
        "teletrabalho": Case(
            When(teletrabalho_exists=True, then=Value("SIM")),
            default=Value("NÃO"),
            output_field=CharField(),
        ),
        "data_inicio_provimento": data_inicio_provimento,
        "data_fim_provimento": data_fim_provimento,
        "cargo_id": F("quadro__cargo__id"),
    }
    mes_atual = datetime.today().date()
    movimentacaoes_ids = (
        CargoQuadro.objects.filter(
            Q(
                Q(cargo__quadro__movimentacaoposse__servidor__ativo=True)
                & Q(cargo__quadro__movimentacaoposse__ativo=True)
            )
            | Q(
                Q(cargo__quadro__movimentacaoposse__data_desligamento__gte=mes_atual)
                | Q(
                    cargo__quadro__movimentacaoposse__servidor__termination_date__gte=mes_atual
                )
            )
            | Q(
                Q(
                    cargo__quadro__movimentacaoposse__servidor__exercise_date__gte=mes_atual
                )
                | Q(cargo__quadro__movimentacaoposse__data_posse__gte=mes_atual)
            )
        )
        .values_list("cargo__quadro__movimentacaoposse", flat=True)
        .distinct()
    )

    movimentacoes = MovimentacaoPosse.objects.filter(
        id__in=list(movimentacaoes_ids)
    ).exclude(servidor__type_by_possession__in=["MAP", "SAP", "APO", "EFP", "BFP"])
    servidores = movimentacoes.annotate(**annotation).values(
        "SERVIDOR_ID",
        "matricula",
        "servidor_ativo",
        "servidor_nome",
        "tipo_posse",
        "cargo",
        "lotacao",
        "data_de_inicio",
        "teletrabalho",
        "data_inicio_provimento",
        "data_fim_provimento",
    )

    if (
        params.get("cargos")
        and len(params.get("cargos")) > 0
        and params.get("cargos")[0] != ""
    ):
        servidores = servidores.filter(cargo_id__in=params.get("cargos"))

    if params.get("keyword") and not (
        params.get("cargos")
        and len(params.get("cargos")) > 0
        and params.get("cargos")[0] != ""
    ):
        servidores = servidores.filter(cargo__icontains=params.get("keyword"))

    if params.get("filtros"):
        values = params.get("filtros")[0].get("value")
        servidores = servidores.filter(quadro__cargo__tipo_lei_cargo__in=values)

    servidores = servidores.distinct()
    for servidor in servidores:
        servidor["lotacao"] = servidor.get("lotacao") or "NÃO HÁ"
        for posse in tipo_posse:
            servidor["tipo_posse"] = (
                posse.get("label")
                if servidor.get("tipo_posse") == posse.get("cvalue")
                else servidor.get("tipo_posse")
            )

    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    return {
        "data": servidores,
        "title": "CONSULTA CARGOS VAGOS E OCUPADOS",
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
        "user": params.get("user"),
        "keys": report_keys,
    }


def formatar_data_por_query(campo):
    consulta = {f"{campo}__isnull": False}
    data_formatada = Case(
        When(
            Q(**consulta),
            then=(
                Concat(
                    LPad(
                        Cast(
                            ExtractDay(F(campo), output_field=CharField()),
                            output_field=CharField(),
                        ),
                        2,
                        Value("0"),
                    ),
                    Value("/"),
                    LPad(
                        Cast(
                            ExtractMonth(F(campo), output_field=CharField()),
                            output_field=CharField(),
                        ),
                        2,
                        Value("0"),
                    ),
                    Value("/"),
                    ExtractYear(campo, output_field=CharField()),
                )
            ),
        ),
        default=Value(""),
    )
    return data_formatada


def count_servidores(types, exclude=None):
    cargo_servidor = "cargo__quadro__movimentacaoposse__servidor"
    filters = {
        f"{cargo_servidor}__type_by_possession__in": types,
        f"{cargo_servidor}__ativo": True,
        "cargo__quadro__movimentacaoposse__ativo": True,
    }
    query = Count(cargo_servidor, filter=Q(**filters))
    if exclude:
        query = Count(
            cargo_servidor,
            filter=Q(
                ~Q(
                    cargo__quadro__movimentacaoposse__servidor__type_by_possession__in=exclude
                ),
                **filters,
            ),
        )

    return query


def get_sintetico_annotation():
    membro_types = ["MBR", "MEL", "MCM", "MEC"]
    efetivo_comissionado_types = ["ECM"]
    servidor_efetivo_types = ["EFE"]
    comissionado_types = ["CMS", "RCM"]
    exclude_aposentados = ["MAP", "SAP", "APO", "EFP", "BFP"]
    sem_vinculo_exclude = [
        *membro_types,
        *efetivo_comissionado_types,
        *comissionado_types,
        *servidor_efetivo_types,
        *exclude_aposentados,
    ]
    cargo_servidor = "cargo__quadro__movimentacaoposse__servidor"
    mes_atual = datetime.today().date()

    sem_vinculo_count = Count(
        cargo_servidor,
        filter=Q(
            ~Q(
                cargo__quadro__movimentacaoposse__servidor__type_by_possession__in=sem_vinculo_exclude
            ),
            cargo__quadro__movimentacaoposse__servidor__ativo=True,
            cargo__quadro__movimentacaoposse__ativo=True,
        ),
    )
    pedidos_nomeacao = Count(
        cargo_servidor,
        filter=Q(
            Q(cargo__quadro__movimentacaoposse__servidor__exercise_date__gte=mes_atual)
            | Q(cargo__quadro__movimentacaoposse__data_posse__gte=mes_atual),
            cargo__quadro__movimentacaoposse__servidor__ativo=True,
        ),
    )
    pedidos_exoneracao = Count(
        cargo_servidor,
        filter=Q(
            Q(
                cargo__quadro__movimentacaoposse__servidor__termination_date__gte=mes_atual
            )
            | Q(cargo__quadro__movimentacaoposse__data_desligamento__gte=mes_atual),
        ),
    )
    vagos = ExpressionWrapper(
        (
            F("existentes")
            - F("membro")
            - F("servidor")
            - F("efetivo_em_comissao")
            - F("comissionado")
            - F("sem_vinculo")
        ),
        output_field=IntegerField(),
    )
    saldo = ExpressionWrapper(
        (F("vagos") - F("pedidos_nomeacao")) + F("pedidos_exoneracao"),
        output_field=IntegerField(),
    )
    existentes = Case(
        When(quantidade_vagas=0, then=count_servidores(["REQ"])),
        default=Coalesce("quantidade_vagas", Value(0)),
    )

    annotation = {
        "cargo_nome": F("cargo__nome"),
        "existentes": existentes,
        "membro": count_servidores(membro_types),
        "servidor": count_servidores(servidor_efetivo_types, membro_types),
        "efetivo_em_comissao": count_servidores(efetivo_comissionado_types),
        "comissionado": count_servidores(comissionado_types),
        "sem_vinculo": sem_vinculo_count,
        "vagos": vagos,
        "pedidos_nomeacao": pedidos_nomeacao,
        "pedidos_exoneracao": pedidos_exoneracao,
        "saldo": saldo,
    }

    return annotation
