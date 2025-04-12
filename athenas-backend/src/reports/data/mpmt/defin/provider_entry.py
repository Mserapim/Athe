import base64
from datetime import datetime
from django.db.models import Q
from rh.defin.models import PFProviderEntry
from contrib.utils import getLogger

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


def get_data_report(params):
    query = PFProviderEntry.objects.filter()

    data = []

    # Extract params
    _competence = params["competence"]
    output_format = params["output_format"]

    # ADD filters
    filter = []
    if _competence:
        month, year = validate_period_format(_competence)
        filter.append(Q(pay_day__month=int(month), pay_day__year=int(year)))

    q_filter = None
    for qf in filter:
        if not q_filter:
            q_filter = qf
        else:
            q_filter = q_filter & qf
    if q_filter:
        query = query.filter(q_filter)

    # Generate data dict
    if output_format == "PDF":
        pass

    if output_format == "XLS":
        for pf in query:
            data.append(
                {
                    "Nome": pf.natural_person.social_name,
                    "CPF": pf.natural_person.cpf,
                    "email": pf.natural_person.email_institucional,
                    "Data de nascimento": (
                        pf.natural_person.data_nascimento.strftime("%d/%m/%Y")
                        if pf.natural_person.data_nascimento
                        else ""
                    ),
                    "CBO": f"{pf.cbo}" if pf.cbo else "",
                    "Lotação": str(pf.workplace) if pf.workplace else "",
                    "Natureza da Atividade": (
                        pf.get_nature_activity_display() if pf.nature_activity else ""
                    ),
                    "Dia do Pagamento": (
                        pf.pay_day.strftime("%d/%m/%Y") if pf.pay_day else ""
                    ),
                    "Valor Bruto": f"R$ {pf.gross_value}",
                    "Isento INSS": "SIM" if pf.inss_exempt else "Não",
                    "Contribuição em Outro Local": "SIM" if pf.contributed else "Não",
                    "Valor Contribuição Parcial": f"R$ {pf.partial_contribution}",
                    "Valor Líquido": f"R$ {pf.liquid_value}",
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
            "Nome",
            "CPF",
            "email",
            "Data de nascimento",
            "CBO",
            "Lotação",
            "Natureza da Atividade",
            "Dia do Pagamento",
            "Valor Bruto",
            "Isento INSS",
            "Contribuição em Outro Local",
            "Valor Contribuição Parcial",
            "Valor Líquido",
        ],
    }
    return values
