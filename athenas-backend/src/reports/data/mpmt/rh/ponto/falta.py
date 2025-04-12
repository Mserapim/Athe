import base64
from datetime import datetime
from django.db.models import Q

from rh.models import MovimentacaoTeletrabalho, Servidor
from standard.models import Choice, JustificationItem
from rh.ponto.models import Falta
from rh.pvf.models import SendingTimeSheet

from rh.pvf.const import STS_EFFECTIVE

from contrib.utils import getLogger

log = getLogger(__name__)


def get_data_report(params):
    """
    Estrutura do relatório:
    matricula
    nome
    categoria (type_by_possession)
    data início
    data fim
    dias
    competência de desconto
    data de processamento
    motivo (justificativa)
    observação
    situação
    total
    """

    data = []
    _servidor = params.get("servidor", None)
    _falta_data_inicio = params.get("falta_data_inicio", None)
    _falta_data_fim = params.get("falta_data_fim", None)

    output_format = params["output_format"]
    order_list = []
    total = 0
    serv_nada_consta = False

    faltas = filter_data(params)
    if faltas.count() > 0:
        serv_nada_consta = False
        total = faltas.count()
        for falta in faltas:
            matricula = falta.servidor.matricula
            nome = falta.servidor.pessoa_fisica.nome

            categoria = Choice.objects.get(
                app_label="rh",
                name="CLASSIF_EMPLOYEE_BY_POSSESSION",
                cvalue=falta.servidor.type_by_possession,
            ).label

            data_inicio = falta.data.strftime("%d/%m/%Y")
            data_fim = (
                falta.data_fim.strftime("%d/%m/%Y")
                if falta.data_fim
                else falta.data.strftime("%d/%m/%Y")
            )
            if falta.data_fim:
                qtd_dias = falta.data_fim - falta.data
                dias = qtd_dias.days + 1
            else:
                dias = 1

            competencia_desconto = falta.competencia_desconto
            data_processado = (
                falta.data_processado.strftime("%d/%m/%Y")
                if falta.data_processado
                else ""
            )

            motivo = "Injustificado"
            if falta.point_justification.exists():
                motivo = JustificationItem.objects.get(
                    value=falta.point_justification.last().reason_type
                ).name

            observacao = falta.observacao
            situacao = Choice.objects.get(
                app_label="ponto", name="SITUATION_CHOICES", cvalue=falta.situacao
            ).label

            if output_format == "PDF":
                data.append(
                    {
                        "matricula": matricula,
                        "nome": nome,
                        "categoria": categoria,
                        "data_inicio": data_inicio,
                        "data_fim": data_fim,
                        "dias": dias,
                        "competencia_desconto": competencia_desconto,
                        "data_processado": data_processado,
                        "motivo": motivo,
                        "observacao": observacao,
                        "situacao": situacao,
                    }
                )

            if output_format == "CSV":
                data.append(
                    {
                        "MATRICULA": matricula,
                        "NOME": nome,
                        "CATEGORIA": categoria,
                        "DATA INICIO": data_inicio,
                        "DATA FIM": data_fim,
                        "DIAS": dias,
                        "COMPETENCIA DE DESCONTO": competencia_desconto,
                        "DATA PROCESSADO": data_processado,
                        "MOTIVO": motivo,
                        "OBSERVACAO": observacao,
                        "SITUACAO": situacao,
                    }
                )

                order_list = [
                    "MATRICULA",
                    "NOME",
                    "CATEGORIA",
                    "DATA INICIO",
                    "DATA FIM",
                    "DIAS",
                    "COMPETENCIA DE DESCONTO",
                    "DATA PROCESSADO",
                    "MOTIVO",
                    "OBSERVACAO",
                    "SITUACAO",
                ]
    elif _servidor:
        serv_nada_consta = True
        servidor = Servidor.objects.get(pk=_servidor)
        matricula = servidor.matricula
        nome = servidor.pessoa_fisica.nome

        lsts = (
            SendingTimeSheet.objects.filter(
                employee=servidor, status__in=[STS_EFFECTIVE]
            )
            .order_by("-reference_year", "-reference_month")
            .first()
        )
        ultimo_folha_ponto_enviado = (
            f"{lsts.reference_month}/{lsts.reference_year}"
            if lsts
            else "Não Encontrado"
        )

        if MovimentacaoTeletrabalho.objects.filter(
            servidor=servidor, ativo=True
        ).exists():
            teletrabalho = MovimentacaoTeletrabalho.objects.filter(
                servidor=servidor, ativo=True
            ).last()
            txt_teletrabalho = f'Sim, de {teletrabalho.data_inicio.strftime("%d/%m/%Y")} até {teletrabalho.data_fim.strftime("%d/%m/%Y") if teletrabalho.data_fim else "-"}'
        else:
            txt_teletrabalho = "Não"

        if _falta_data_inicio:
            _falta_data_inicio = datetime.strptime(_falta_data_inicio, "%Y-%m-%d")
            falta_dt_inicio = _falta_data_inicio.strftime("%d/%m/%Y")
        else:
            falta_dt_inicio = ""

        if _falta_data_fim:
            _falta_data_fim = datetime.strptime(_falta_data_fim, "%Y-%m-%d")
            falta_dt_fim = _falta_data_fim.strftime("%d/%m/%Y")
        else:
            falta_dt_fim = ""

        if output_format == "PDF":
            data.append(
                {
                    "matricula": matricula,
                    "nome": nome,
                    "periodo": f"{falta_dt_inicio} até {falta_dt_fim}",
                    "ultimo_folha_ponto_enviado": ultimo_folha_ponto_enviado,
                    "teletrabalho": txt_teletrabalho,
                }
            )
    else:
        serv_nada_consta = False
        if output_format == "PDF":
            data.append(
                {
                    "matricula": "",
                    "nome": "",
                    "categoria": "",
                    "data_inicio": "",
                    "data_fim": "",
                    "dias": "",
                    "competencia_desconto": "",
                    "data_processado": "",
                    "motivo": "",
                    "observacao": "",
                    "situacao": "",
                }
            )
        if output_format == "CSV":
            data.append(
                {
                    "MATRICULA": "",
                    "NOME": "",
                    "CATEGORIA": "",
                    "DATA INICIO": "",
                    "DATA FIM": "",
                    "DIAS": "",
                    "COMPETENCIA DE DESCONTO": "",
                    "DATA PROCESSADO": "",
                    "MOTIVO": "",
                    "OBSERVACAO": "",
                    "SITUACAO": "",
                }
            )

            order_list = [
                "MATRICULA",
                "NOME",
                "CATEGORIA",
                "DATA INICIO",
                "DATA FIM",
                "DIAS",
                "COMPETENCIA DE DESCONTO",
                "DATA PROCESSADO",
                "MOTIVO",
                "OBSERVACAO",
                "SITUACAO",
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
        "total": f"Total: {total}",
        "serv_nada_consta": serv_nada_consta,
    }

    return values


def filter_data(params):
    # Extract params
    _servidor = params.get("servidor", None)
    _tipo_falta = params.get("tipo_falta", None)
    _situacao = params.get("situacao", None)
    _impacto_financeiro = params.get("impacto_financeiro", None)
    _competencia_desconto = params.get("competencia_desconto", None)
    _proce_data_inicio = params.get("proce_data_inicio", None)
    _proce_data_fim = params.get("proce_data_fim", None)
    _falta_data_inicio = params.get("falta_data_inicio", None)
    _falta_data_fim = params.get("falta_data_fim", None)
    _types_by_possession = params.get("types_by_possession", None)

    # Apply filters
    _filter = []

    if _servidor:
        _filter.append(Q(servidor__pk=_servidor))

    if _tipo_falta:
        justificado = True if int(_tipo_falta) == 1 else False
        _filter.append(Q(justificado=justificado))

    if _situacao:
        _filter.append(Q(situacao=_situacao))

    if _impacto_financeiro:
        impacto_financeiro = True if int(_impacto_financeiro) == 1 else False
        _filter.append(Q(payroll=impacto_financeiro))

    if _competencia_desconto:
        _filter.append(Q(competencia_desconto=_competencia_desconto))

    if _proce_data_inicio:
        _filter.append(
            Q(
                data_processado__gte=datetime.strptime(
                    _proce_data_inicio, "%Y-%m-%d"
                ).date()
            )
        )

    if _proce_data_fim:
        _filter.append(
            Q(
                data_processado__lte=datetime.strptime(
                    _proce_data_fim, "%Y-%m-%d"
                ).date()
            )
        )

    if _falta_data_inicio:
        _filter.append(
            Q(data__gte=datetime.strptime(_falta_data_inicio, "%Y-%m-%d").date())
        )

    if _falta_data_fim:
        _filter.append(
            Q(data_fim__lte=datetime.strptime(_falta_data_fim, "%Y-%m-%d").date())
        )

    if _types_by_possession and not _servidor:
        types_by_possession = _types_by_possession.split(",")
        _filter.append(Q(servidor__type_by_possession__in=types_by_possession))

    q_filter = None
    for qf in _filter:
        if not q_filter:
            q_filter = qf
        else:
            q_filter = q_filter & qf

    if q_filter:
        faltas = Falta.objects.filter(q_filter).order_by(
            "servidor__pessoa_fisica__nome"
        )

    return faltas
