from contrib.utils import getLogger
from datetime import datetime
import base64

from rh.models import BenefitMovement

log = getLogger(__name__)


def get_data_report(params):
    """
    Função que retorna um dicionário de dados necessários à geração do relatório
    """
    ativo = params.get("ativo")
    cargo = params.get("cargo")
    servidor = params.get("servidor")
    paridade_salarial = params.get("paridade_salarial")
    beneficio_integral = params.get("beneficio_integral")

    query = BenefitMovement.objects.all()

    data = []

    if ativo is not None and ativo != "":
        if ativo == "SIM":
            query = query.filter(ativo=True)
        else:
            query = query.filter(ativo=False)

    if cargo is not None and cargo != "":
        query = query.filter(quadro__cargo__pk=int(cargo))

    if servidor is not None and servidor != "":
        query = query.filter(servidor__pk=int(servidor))

    if paridade_salarial is not None and paridade_salarial != "":

        if paridade_salarial == "SIM":
            query = query.filter(paridade_salarial=True)
        else:
            query = query.filter(paridade_salarial=False)

    if beneficio_integral is not None and beneficio_integral != "":
        if beneficio_integral == "SIM":
            query = query.filter(beneficio_integral=True)
        else:
            query = query.filter(beneficio_integral=False)

    for mov in query:
        data.append(
            {
                "matricula": mov.servidor.matricula,
                "nome": mov.servidor.pessoa_fisica.social_name,
                "cpf": mov.servidor.pessoa_fisica.cpf,
                "dt_nascimento": (
                    mov.servidor.pessoa_fisica.data_nascimento.strftime("%d/%m/%Y")
                    if mov.servidor.pessoa_fisica.data_nascimento
                    else ""
                ),
                "categoria_funcional": mov.servidor.get_type_by_possession_display(),
                "ato": mov.publicacao_movimentacao.document,
                "proventos_integrais": (
                    "SIM" if mov.beneficio_integral == True else "Não"
                ),
                "paridade": "SIM" if mov.paridade_salarial == True else "Não",
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
        "keys": [
            "matricula",
            "nome",
            "cpf",
            "dt_nascimento",
            "categoria_funcional",
            "ato",
            "proventos_integrais",
            "paridade",
        ],
    }
    return values
