import base64
from datetime import datetime
from django.db.models import Q, Sum

from contrib.utils import getLogger

from diarias.models import PrestacaoContas
from standard.models import Item

log = getLogger(__name__)


def validate_period_format(value):

    try:
        month, year = value.split("/")
        return month, year
    except Exception as e:
        log.error(e)
        raise Exception(
            "A Formatação das competências deve seguir o seguinte padrão: MM/AAAA (Ex.: 08/2023)"
        )


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

    data = {}

    # Extract params
    id_prestacao = params["id_prestacao"]

    output_format = params["output_format"]

    try:
        prestacao = PrestacaoContas.objects.get(id=id_prestacao)
        beneficiario = prestacao.beneficiario
        servidor = beneficiario.servidor
        lotacao = (
            servidor.workplace_only_active.first().lotacao
            if servidor.workplace_only_active.first()
            else ""
        )

        data["matricula"] = servidor.matricula
        data["nome"] = servidor.pessoa_fisica.social_name
        data["cargo"] = get_cargo(servidor, datetime.today().date())
        data["cat_funcional"] = servidor.get_type_by_possession_display()
        data["lotacao"] = lotacao.__str__

        data["prestacao"] = prestacao
        data["beneficiario"] = beneficiario
        data["viagem"] = beneficiario.viagem
        data["calculo"] = beneficiario.calculos_diarias_consolidados
        data["eventos"] = beneficiario.eventos.all()
        data["destinos"] = beneficiario.destinos.all()

    except Exception as e:
        log.info(e)
        raise ValueError(f"Erro ao buscar os dados da Prestação de Contas - {e}")

    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    values = {
        "title": f"Prestação de Contas OS: {beneficiario.codigo_os}",
        "data": data,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
        "keys": [],
    }
    return values
