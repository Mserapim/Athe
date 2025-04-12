from datetime import datetime
from contrib.base_converter import formatar_hora_timedelta
from contrib.middleware import get_current_user
from rh.pvf.const import *
from rh.pvf.models import SendingTimeSheet
from rh.registerpoint.utils.ponto import total_faltas_e_saldo_periodo
from standard.models import Choice, JustificationItem
from contrib.utils import employee_from_user
from datetime import timedelta


def get_request_progress_timesheet():
    """
    Checa se já existe uma solicitação de folha ponto em andamento
    :returns: (bool)
    """
    return (
        SendingTimeSheet.objects.filter(
            employee=employee_from_user(get_current_user()),
        )
        .exclude(
            status__in=[
                STS_REJECTED,
                STS_EFFECTIVE,
                STS_CANCELED_DGP,
                STS_CANCELED_APPLICANT,
            ]
        )
        .exists()
    )


def get_reference_timesheet(employee):
    """
    Lista as referências em que o servidor pode realizar o envio
    :returns: (list)
    """
    references = []
    qtd_reference = Choice.objects.get(app_label="pvf", name="RETROACTIVE_MONTHS").value
    data_year = datetime.today().year
    data_month = datetime.today().month
    count = 0
    while count < qtd_reference:
        if (
            not SendingTimeSheet.objects.filter(
                employee=employee,
                reference_month=data_month,
                reference_year=data_year,
            )
            .exclude(
                status__in=[STS_REJECTED, STS_CANCELED_DGP, STS_CANCELED_APPLICANT]
            )
            .exists()
        ):
            references.append((data_month, data_year))
        data_year = data_year - 1 if data_month == 1 else data_year
        data_month = 12 if data_month == 1 else data_month - 1
        count = count + 1
    obj_reference = []
    for reference in references:
        obj_reference.append({"reference": str(reference[0]) + "/" + str(reference[1])})
    return obj_reference


def get_data_type_by_possession_access(type_by_possession):
    """
    Lista de justificativas do folha ponto conforme o type_by_possesion
    :returns: (list)
    """
    list_items_pk = []
    types_in_justif_item = []
    for item in JustificationItem.objects.all():
        types_in_justif_item = (
            item.type_by_possession.split(",") if item.type_by_possession else None
        )
        if types_in_justif_item and type_by_possession in types_in_justif_item:
            list_items_pk.append(item.pk)
    return list_items_pk


def pending(pk):
    """
    Lista de pendencias do folha ponto
    :returns: (list)
    """

    request = SendingTimeSheet.objects.get(pk=pk)
    employee = request.employee
    month = request.reference_month
    year = request.reference_year
    lack, balance = total_faltas_e_saldo_periodo(month, year, employee)
    pendencies = []
    if lack > 0:
        pendencies.append({"type": "Faltas", "value": lack})
    elif balance < timedelta(0):
        pendencies.append(
            {"type": "Saldo do Período", "value": formatar_hora_timedelta(balance)}
        )

    justifications = request.pvf_request_justification.filter(
        reason_type__in=Choice.objects.filter(
            name="TYPE_OF_REASON_PENDING"
        ).values_list("value", flat=True)
    )
    for justification in justifications:
        pendencies.append(
            {"type": "Justificativas", "value": justification.get_reason_type_str}
        )
    return pendencies


def envio_pendente_folha_ponto(employee):
    """
    Função que verifica se o servidor folha ponto criado e pendente de envio
    Args:
        employee
    Returns:
       list[]:
    """
    folha_ponto = SendingTimeSheet.objects.filter(
        employee=employee, status=STS_STAND_BY
    ).last()
    if folha_ponto:
        return [True, folha_ponto.pk]
    return [False, None]
