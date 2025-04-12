from contrib.br import br_month
from contrib.utils import employee_from_user, getLogger
from rh.models import Servidor
from anotacao_pessoal.models import AnotacaoPessoal
from datetime import datetime
import base64
from rh.models import Servidor
from django.db.models.query_utils import Q


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

    servidor = params["servidor"]
    tipos_anotacao = params.get("tipos_anotacao", None)
    tipos_documentos = params.get("tipos_documentos", None)
    filtro_txt = params.get("filtro_txt", None)

    data = {}

    servidor = Servidor.objects.filter(pk=servidor).first()
    anotacoes_pessoais = AnotacaoPessoal.objects.filter(servidor=servidor)

    if filtro_txt is not None:
        anotacoes_pessoais = anotacoes_pessoais.filter(
            Q(documento_ano__icontains=filtro_txt)
            | Q(documento_numero__icontains=filtro_txt)
        )

    if tipos_anotacao is not None:
        anotacoes_pessoais = anotacoes_pessoais.filter(tipo__in=tipos_anotacao)

    if tipos_documentos is not None:
        anotacoes_pessoais = anotacoes_pessoais.filter(
            documento_tipo__in=tipos_documentos
        )

    lotacao = (
        servidor.workplace_only_active.first().lotacao
        if servidor.workplace_only_active.first()
        else ""
    )

    data["matricula"] = servidor.matricula
    data["nome"] = servidor.pessoa_fisica.social_name
    data["work_role"] = get_cargo(servidor, datetime.today().date())
    data["lotation"] = str(lotacao)
    data["anotacoes_pessoais"] = anotacoes_pessoais

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
