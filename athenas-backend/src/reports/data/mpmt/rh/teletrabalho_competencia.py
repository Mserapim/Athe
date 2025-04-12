from contrib.br import br_month
from contrib.utils import employee_from_user, getLogger
from datetime import datetime, date
import base64
from contrib.utils import QuerySetChain

from rh.teletrabalho.teletrabalho_competencia_utils import (
    get_query_teletrabalho_periodo,
)
from rh.pvf.const import (
    STS_EFFECTIVE,
    STS_WAI_SUBS_SCIENCE,
    STS_WAI_APPROVER,
    STS_WAI_EFFECTIVENESS,
    STS_REJECTED,
    STS_CORREGEDORIE_ADVISORY,
    STS_STAND_BY,
    STS_ESCALA_ENVIADA,
)

log = getLogger(__name__)


def get_data_report(params):
    """
    Função que retorna um dicionário de dados necessários à geração do relatório
    """
    periodo_ano = params["periodo_ano"]
    periodo_mes = params["periodo_mes"]
    filtro = params["filtro"]

    titulo_filtro = ""

    if filtro == "todos":
        titulo_filtro = f" - Todos"
    elif filtro == "efetivada":
        titulo_filtro = f" - Efetivadas"
    elif filtro == "pendente":
        titulo_filtro = f" - Pendentes"

    data = {}

    movimentacoes = get_query_teletrabalho_periodo(params=params)

    if isinstance(movimentacoes, QuerySetChain):
        movimentacoes = movimentacoes._all()

    data["movimentacoes"] = movimentacoes
    data["periodo_ano"] = periodo_ano
    data["periodo_mes"] = periodo_mes

    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    values = {
        "title": params["report_name"]
        + f" {periodo_mes} / {periodo_ano}{titulo_filtro}",
        "data": data,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
    }
    return values
