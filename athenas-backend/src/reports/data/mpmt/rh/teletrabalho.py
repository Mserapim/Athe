import base64

from datetime import datetime

from rh.models import MovimentacaoTeletrabalho, MetaTeletrabalho, Servidor
from rh.models import Servidor
from standard.models import Choice

from django.db.models.query_utils import Q
from reports.data.mpmt.reportmodels.identificationpdf import current_position
from contrib.utils import getLogger


log = getLogger(__name__)


def get_cargo(servidor, reference_date):
    effective = None
    commission = None
    possessions = servidor.posses

    effectives = possessions.filter(
        Q(data_exercicio__lte=reference_date),
        Q(data_desligamento__gt=reference_date) | Q(data_desligamento__isnull=True),
        quadro__cargo__tipo_lei_cargo="EF",
    )
    if effectives.exists():
        ef = effectives.latest("data_exercicio")
        effective = ef.quadro
    if servidor.ativo or (not effective):
        commissions = possessions.filter(
            Q(data_exercicio__lte=reference_date),
            Q(data_desligamento__gt=reference_date) | Q(data_desligamento__isnull=True),
            quadro__cargo__tipo_lei_cargo__in=("CM", "FC"),
        )
        if commissions.exists():
            cm = commissions.latest("data_exercicio")
            commission = cm.quadro
    if not effective and not commission:
        effective = "Não encontrado"
    return str(effective) if effective else str(commission)


def get_data_report(params):
    """
    Função que retorna um dicionário de dados necessários à geração do relatório
    """
    mov_teletrabalho = params["mov_teletrabalho"]
    servidor = params["servidor"]

    data = {}

    servidor = Servidor.objects.filter(pk=servidor).first()
    mov_teletrabalho = MovimentacaoTeletrabalho.objects.filter(
        id=mov_teletrabalho
    ).first()
    metas = MetaTeletrabalho.objects.filter(
        mov_teletrabalho=mov_teletrabalho, active=True
    )

    data["nome"] = servidor.pessoa_fisica.social_name
    data["work_role"] = get_cargo(servidor, mov_teletrabalho.data_inicio)
    data["lotation"] = str(servidor.workplace_only_active.first().lotacao)
    data["mov_teletrabalho"] = mov_teletrabalho
    data["metas"] = []

    for meta in metas:
        data["metas"].append(
            {
                "descricao": meta.descricao,
                "meta": f"{meta.meta} ({meta.get_periodicity_display()})",
                "data_inicio": meta.data_inicio,
                "data_fim": meta.data_fim,
            }
        )

    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    values = {
        "title": params["report_name"],
        "data": data,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
    }
    return values


def get_data_gestor_teletrabalho_report(params):
    """
    Função que retorna um dicionário de dados necessários à geração do relatório
    """
    _tipo_pedido = int(params["tipo_pedido"])
    _tipo_ato = int(params["tipo_ato"])
    _p_ini_dt_ini = params["p_ini_dt_ini"]
    _p_ini_dt_fim = params["p_ini_dt_fim"]
    _p_fim_dt_ini = params["p_fim_dt_ini"]
    _p_fim_dt_fim = params["p_fim_dt_fim"]
    _output_format = params["output_format"]

    order_list = []
    data = []
    _filter = []
    q_filter = None

    if _tipo_pedido:
        if _tipo_pedido == 9999:
            _filter.append(
                Q(
                    tipo_pedido__in=[
                        int(item)
                        for item in Choice.objects.filter(
                            app_label="rh", name="TIPO_PEDIDO"
                        ).values_list("cvalue", flat=True)
                    ]
                )
            )
        else:
            _filter.append(Q(tipo_pedido=_tipo_pedido))

    if _tipo_ato:
        if _tipo_ato == 9999:
            _filter.append(
                Q(
                    tipo_ato__in=[
                        int(item)
                        for item in Choice.objects.filter(
                            app_label="rh", name="TYPE_ACT"
                        ).values_list("cvalue", flat=True)
                    ]
                )
            )
        else:
            _filter.append(Q(tipo_ato=_tipo_ato))

    # Pesquisa por período inicial e final
    if _p_ini_dt_ini and _p_ini_dt_fim and _p_fim_dt_ini and _p_fim_dt_fim:
        _filter.append(
            Q(
                Q(
                    data_inicio__gte=_p_ini_dt_ini,
                    data_inicio__lte=_p_ini_dt_fim,
                )
                & Q(
                    data_fim__gte=_p_fim_dt_ini,
                    data_fim__lte=_p_fim_dt_fim,
                )
            )
        )
    else:
        # Pesquisa por período inicial
        if _p_ini_dt_ini and _p_ini_dt_fim:
            _filter.append(
                Q(
                    data_inicio__gte=_p_ini_dt_ini,
                    data_inicio__lte=_p_ini_dt_fim,
                )
            )
        elif _p_ini_dt_ini:
            _filter.append(
                Q(
                    data_inicio__gte=_p_ini_dt_ini,
                )
            )
        elif _p_ini_dt_fim:
            _filter.append(
                Q(
                    data_inicio__lte=_p_ini_dt_fim,
                )
            )

        # Pesquisa por período final
        if _p_fim_dt_ini and _p_fim_dt_fim:
            _filter.append(
                Q(
                    data_fim__gte=_p_fim_dt_ini,
                    data_fim__lte=_p_fim_dt_fim,
                )
            )
        elif _p_fim_dt_ini:
            _filter.append(
                Q(
                    data_fim__gte=_p_fim_dt_ini,
                )
            )
        elif _p_fim_dt_fim:
            _filter.append(
                Q(
                    data_fim__lte=_p_fim_dt_fim,
                )
            )

    for qf in _filter:
        if not q_filter:
            q_filter = qf
        else:
            q_filter = q_filter & qf

    if q_filter:
        query = MovimentacaoTeletrabalho.objects.filter(q_filter).order_by(
            "data_inicio"
        )

        if query.exists():
            for mov_tele in query:
                if _output_format in ["PDF", "XLS"]:
                    data.append(
                        {
                            "matricula": mov_tele.servidor.matricula,
                            "nome": mov_tele.servidor.pessoa_fisica.nome,
                            "cpf": mov_tele.servidor.pessoa_fisica.cpf,
                            "cargo_atual": current_position(mov_tele.servidor),
                            "lotacao": (
                                mov_tele.lotacao.__str__() if mov_tele.lotacao else ""
                            ),
                            "tipo_pedido": mov_tele.get_tipo_pedido_display(),
                            "tipo_ato": mov_tele.get_tipo_ato_display(),
                            "gedoc": mov_tele.gedoc,
                            "dt_inicio_exercicio": mov_tele.data_inicio.strftime(
                                "%d/%m/%Y"
                            ),
                            "dt_fim_exercicio": mov_tele.data_fim.strftime("%d/%m/%Y"),
                            "aprovador": mov_tele.aprovador.__str__(),
                        }
                    )
                elif _output_format == "CSV":
                    data.append(
                        {
                            "MATRICULA": mov_tele.servidor.matricula,
                            "NOME": mov_tele.servidor.pessoa_fisica.nome,
                            "CPF": mov_tele.servidor.pessoa_fisica.cpf,
                            "CARGO ATUAL": current_position(mov_tele.servidor),
                            "LOTACAO": mov_tele.lotacao if mov_tele.lotacao else "",
                            "TIPO DO PEDIDO": mov_tele.get_tipo_pedido_display(),
                            "TIPO DO ATO": mov_tele.get_tipo_ato_display(),
                            "GEDOC": mov_tele.gedoc,
                            "DATA INICIO DE EXERCICIO": mov_tele.data_inicio.strftime(
                                "%d/%m/%Y"
                            ),
                            "DATA FIM DE EXERCICIO": mov_tele.data_fim.strftime(
                                "%d/%m/%Y"
                            ),
                            "APROVADOR": mov_tele.aprovador,
                        }
                    )

                order_list = [
                    "MATRICULA",
                    "NOME",
                    "CPF",
                    "CARGO ATUAL",
                    "LOTACAO",
                    "TIPO DO PEDIDO",
                    "TIPO DO ATO",
                    "GEDOC",
                    "DATA INICIO DE EXERCICIO",
                    "DATA FIM DE EXERCICIO",
                    "APROVADOR",
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
