from contrib.utils import getLogger
from standard.models import Choice
from rh.dayoff.models import Usufruct, AcquisitionPeriod
from rh.dayoff.const import USU_SOLD
from rh.dayoff.models import Activity

log = getLogger(__name__)


def get_list_of_non_retifications_usufructs():
    """
    Função que consulta Parâmetro do Sistema que verifica quais itens não serão passíveis de retificação e retorna em uma lista.
    :returns: (list)
    """
    try:
        list_exclude_usufruct = Choice.objects.filter(
            name="PVF_SUB_CONFIGURATION_EXCLUDE_USUFRUCT", active=True
        ).values_list("value")
        ids_exclude_usufruct = [x[0] for x in list_exclude_usufruct]
        return ids_exclude_usufruct
    except Exception as e:
        log.error(e)


def get_sold_usufructs_date(acq_period):
    """
    Função que verifica se já houve o gozo da primeira parcela dento do período aquisitivo e retorna lista com as 'pk' dos usufrutos vendidos e recebidos
    :returns: (list)
    """
    try:
        list_of_started_acq_per = [x[0] for x in acq_period]
        sold_usufruted = Usufruct.objects.filter(
            activity__acquisition_period__id__in=list_of_started_acq_per,
            status=USU_SOLD,
        ).values_list("pk")
        return [x[0] for x in sold_usufruted]
    except Exception as e:
        log.error(e)


def totally_paid_periods(employee):
    """
    Retorna uma lista de pk's dos períodos aquisitivos que tiveram todos os dias vendidos, filtrados pelo servidor
    :returns:
    list_of_totally_paid_periods (list)
    """
    list_of_totally_paid_periods = []
    acq_periods = AcquisitionPeriod.objects.filter(employee=employee)
    for acq in acq_periods:
        if acq.days == acq.paid_days:
            list_of_totally_paid_periods.append(acq.pk)
    return list_of_totally_paid_periods


def extract_selections_usufructs(ids):
    """
    Retorna uma lista de dados dos usufrutos a serem retificados.
    :returns: (list)
    """
    modifieds = []
    days_usufructs = 0
    all_modifieds = []
    total_days = 0
    if ids:
        usufructs = Usufruct.objects.filter(id__in=ids)
        for usufruct in usufructs:
            if usufruct.start_date:
                modifieds.append(usufruct.pk)
                days_usufructs = days_usufructs + usufruct.days

            all_modifieds.append(usufruct.pk)
            total_days = total_days + usufruct.days

    return [modifieds, all_modifieds, total_days, days_usufructs]


def usufrutos_retificados_ids(solicitacao_id):
    """
    Retorna os ids dos usufrutos que serão retificados da solicitação
    :retorno: (list)
    """
    usu_modificados = Activity.objects.filter(
        activity_requests__pk=solicitacao_id
    ).values_list("modifieds__pk", flat=True)
    usu_modificados_venda = Activity.objects.filter(
        activity_requests__pk=solicitacao_id, usufructs__start_date__isnull=True
    ).values_list("usufructs__pk", flat=True)
    usu_modificados = [x for x in list(usu_modificados) if x != None]
    return usu_modificados + list(usu_modificados_venda)
