import re
import base64
from datetime import datetime
from django.db.models import Q
from rh.gfp.models import ExtensionSalaryProgression, MovimentacaoProgressao

from contrib.utils import getLogger
from rh.models import MovimentacaoTeletrabalho

log = getLogger(__name__)


def current_position(employee):
    if employee.get_posses_ativas().count() > 0:
        if employee.get_is_comissionado():
            possesion = employee.posses_ativas.filter(
                quadro__cargo__tipo_lei_cargo="CM"
            ).first()
            return possesion.quadro.cargo.nome
        elif employee.get_is_eletivo():
            possesion = employee.posses_ativas.filter(
                quadro__cargo__tipo_lei_cargo="EL"
            ).first()
            return possesion.quadro.cargo.nome
        else:
            if employee.get_posses_ativas().first().quadro:
                return employee.get_posses_ativas().first().quadro.cargo.nome

    return ""


def get_data_report(params: dict) -> dict:
    """
    Função responsável pela geração de dados do relatório,
    aplica-se os filtros e organiza os dados a serem retornados
    :returns: (dict)
    """

    data = []

    # Extract params
    year = int(params["year"])
    month = int(params["month"])
    output_format = params["output_format"]
    progressed = params["progressed"]
    # get query
    if progressed:
        query = (
            MovimentacaoProgressao.objects.filter(
                data_fim_vigencia__year=year,
                data_fim_vigencia__month=month,
                servidor__tipo="S",
                servidor__ativo=True,
            )
            .exclude(referencia_nivel2d__cargos_estrutura__cargo__tipo_lei_cargo="CM")
            .order_by("expected_date")
        )

        filtered = (x.pk for x in query if x.next_type_progression != "V")

        query = query.filter(pk__in=filtered)

    else:
        query = (
            MovimentacaoProgressao.objects.filter(
                expected_date__year=year,
                expected_date__month=month,
                servidor__tipo="S",
                servidor__ativo=True,
                expected_date__isnull=False,
                ativo=True,
            )
            .exclude(referencia_nivel2d__cargos_estrutura__cargo__tipo_lei_cargo="CM")
            .order_by("expected_date")
        )

        filtered = (x.pk for x in query if x.next_type_progression != "V")

        query = query.filter(pk__in=filtered)

    if output_format == "PDF":
        for progression in query:

            teletrabalho = MovimentacaoTeletrabalho.objects.filter(
                Q(
                    Q(data_inicio__month__lte=int(month), data_inicio__year=int(year))
                    | Q(data_inicio__year__lt=int(year))
                )
                & Q(
                    Q(
                        Q(data_fim__month__gt=int(month), data_fim__year=int(year))
                        | Q(data_fim__year__gt=int(year))
                    )
                    | Q(data_fim__isnull=True)
                ),
                servidor=progression.servidor,
            )

            progression_data_report = {
                "name": progression.servidor.pessoa_fisica.nome,
                "register": progression.servidor.matricula,
                "expected_date": (
                    progression.expected_date.strftime("%d/%m/%Y")
                    if progression.expected_date
                    else ""
                ),
                "telework": "Sim" if teletrabalho.exists() else "Não",
                "imediate_boss": (
                    progression.servidor.chefe_imediato.pessoa_fisica.nome
                    if progression.servidor.chefe_imediato
                    else ""
                ),
                "work_role": current_position(progression.servidor),
            }

            data.append(progression_data_report)

    if output_format == "XLS":
        for progression in query:

            teletrabalho = MovimentacaoTeletrabalho.objects.filter(
                Q(
                    Q(data_inicio__month__lte=int(month), data_inicio__year=int(year))
                    | Q(data_inicio__year__lt=int(year))
                )
                & Q(
                    Q(
                        Q(data_fim__month__gt=int(month), data_fim__year=int(year))
                        | Q(data_fim__year__gt=int(year))
                    )
                    | Q(data_fim__isnull=True)
                ),
                servidor=progression.servidor,
            )

            progression_data_report = {
                "Nome": progression.servidor.pessoa_fisica.nome,
                "Matrícula": progression.servidor.matricula,
                "Data Prevista": (
                    progression.expected_date.strftime("%d/%m/%Y")
                    if progression.expected_date
                    else ""
                ),
                "Teletrabalho": "Sim" if teletrabalho.exists() else "Não",
                "Chefe Imediato": (
                    progression.servidor.chefe_imediato.pessoa_fisica.nome
                    if progression.servidor.chefe_imediato
                    else ""
                ),
                "Cargo": current_position(progression.servidor),
            }

            data.append(progression_data_report)

    if output_format == "CSV":
        pass

    order_list = [
        "Nome",
        "Matrícula",
        "Data Prevista",
        "Teletrabalho",
        "Chefe Imediato",
        "Cargo",
    ]
    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    values = {
        "title": params["report_name"],
        "data": data,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
        "keys": order_list,
    }
    return values


def strip_html_tags(text):
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def get_data(params: dict) -> dict:
    """
    Função responsável pela geração de dados do relatório de prorrogados,
    aplica-se os filtros e organiza os dados a serem retornados
    :returns: (dict)
    """

    data = []

    progressoes_str = params.get("progressao", "[]")
    if progressoes_str:
        progressoes_str = progressoes_str[0]
        progressoes_list = [int(x) for x in progressoes_str.strip("[]").split(",")]
    else:
        progressoes_list = []

    query = MovimentacaoProgressao.objects.filter(id__in=progressoes_list)

    if params.get("title") == "Relatório de Prorrogações":
        for movimentacao in query:
            query = ExtensionSalaryProgression.objects.filter(
                progression__servidor=movimentacao.servidor,
                progression__referencia_nivel2d=movimentacao.referencia_nivel2d,
            ).order_by("progression__servidor__pessoa_fisica__nome")
            for extension in query:
                progression = extension.progression
                extension = extension
                motivo = strip_html_tags(extension.purpose) if extension else ""
                data_prevista_anterior = progression.expected_date
                data_referencia_anterior = progression.data_referencia
                prorrogacoes_data = {
                    "matricula": progression.servidor.matricula,
                    "nome": progression.servidor.pessoa_fisica.nome,
                    "referencia": progression.referencia_nivel2d,
                    "data_prevista_anterior": (
                        data_prevista_anterior.strftime("%d/%m/%Y")
                        if data_prevista_anterior
                        else ""
                    ),
                    "data_prevista_atual": (
                        movimentacao.expected_date.strftime("%d/%m/%Y")
                        if movimentacao.expected_date
                        else ""
                    ),
                    "data_referencia_anterior": (
                        data_referencia_anterior.strftime("%d/%m/%Y")
                        if data_referencia_anterior
                        else ""
                    ),
                    "data_referencia_atual": (
                        movimentacao.data_referencia.strftime("%d/%m/%Y")
                        if movimentacao.data_referencia
                        else ""
                    ),
                    "motivo": motivo,
                }
                data.append(prorrogacoes_data)

        order_list = [
            "Matrícula",
            "Nome",
            "Referência",
            "Data Prevista Anterior",
            "Data Prevista Atual",
            "Data Referência Anterior",
            "Data Referência Atual",
            "Motivo",
        ]

    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    values = {
        "title": params["report_name"],
        "data": data,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
        "keys": order_list,
    }
    return values
