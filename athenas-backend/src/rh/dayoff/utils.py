# -*- coding: utf-8 -*-

from common.usefulday.models import ParseNonWorkingDay
from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from contrib.middleware import get_current_user
from engine.notification.models import Notification
from rh.utils import send_mail_and_notify
from rh.dayoff.const import INDIVIDUAL_VACATION


log = getLogger(__name__)


def action_check(action, status, status_map={}, status_map_str={}):
    """Este método checa se a ação é possível de acordo com um dict de estados, ações e estados de destino.

    Args:
        activity (str): Ação
        status (int): Estado atual
        status_map (dict): Mapa dos estados
    Returns:
        list: list of status
    """
    rs_action = None
    if (status in status_map.keys()) and (action in status_map.get(status, ())):
        rs_action = status_map.get(status, {}).get(action)
        if type(rs_action) is tuple and len(rs_action) > 1:
            for perm in rs_action[1]:
                if get_current_user().has_perm(perm):
                    return rs_action[0]
        else:
            return status_map.get(status, {}).get(action)
    buff = "não encontradas"
    for key in status_map.get(status, {}).keys():
        buff = "%s" % key
        if rs_action and type(rs_action) is tuple and len(rs_action) > 1:
            buff = "%s => %s, permissões requeridas:" % (
                buff,
                status_map_str.get(rs_action[0]),
            )
            for perm in rs_action[1]:
                buff = "%s %s" % (buff, perm)
        elif rs_action:
            buff = "%s => %s" % (buff, status_map_str.get(rs_action))
    allowed = buff
    raise Exception(
        "Transição inválida: estado(%s) não permite ação (%s)! Ações permitidas (%s)."
        % (status_map_str.get(status, status), action, allowed)
    )


def status_transition_check(status, target, status_map={}):
    """Este método checa se o target(estado de destino) está dentro dos estados de destino possíveis para o estado atual.

    Args:
        status (int): Estado atual
        target (int): Estado alvo
        status_map (dict): Mapa dos estados
    Returns:
        bool: True/False
    Raise:
        Exception: raise exception quando a não encontra possibilidade
    """
    actions = status_map.get(status)
    chance = []
    for st in actions.keys():
        if actions.get(st):
            if type(actions.get(st)) in (list, tuple):
                for x in actions.get(st):
                    chance.append(x)
            else:
                chance.append(actions.get(st))
    if target in chance:
        return chance
    raise Exception(
        "Transição inválida: estado (%s) não é possível para (%s) não existe!"
        % (target, actions)
    )


def working_days(date_range=None):
    """
    Este método calcula a quantidade de dias úteis de um NewDateRange descontando os feriados e fins de semana no período.

    Args:
        date_range (NewDateRange): NewDateRange do intervalo que deve ser calculado.
    Returns:
        int: quantidade de dias
    """
    if date_range is None:
        raise Exception("NewDateRange não informado.")
    holidays = len(ParseNonWorkingDay.national_holidays(date_range=date_range))
    work_days = 0
    for data in date_range.iter():
        if not NewDateRange.day_weekend(data):
            work_days += 1
    work_days = work_days - holidays
    return work_days if work_days > 0 else 0


def notify(
    msg_or_mid, target, sender=None, types=["SYS"], notification_cfg="", **kargs
):
    """
    This method is responsible to identify wihch notification type will be send.
    This method based in standard.models.Configuration and configurations for 'ferias'.
    """

    try:
        Notification.notify(msg_or_mid, target, sender=sender, types=types, **kargs)
    except Exception as err:
        log.exception(err)
        send_mail_and_notify(source="Err", message=str(err), err=err)


def competence_paid_unicode(usu):
    if usu.type_usufruct == INDIVIDUAL_VACATION:
        texto_parcela = (
            f"{usu.payment_competence}| (PENDENTE)"
            if usu.payment_month and usu.payment_year
            else ""
        )
    else:
        texto_parcela = (
            f"{usu.payment_competence}| {usu.payment_installments}(PENDENTE)"
            if usu.payment_month and usu.payment_year
            else ""
        )
    return usu.competence_paid if usu.competence_paid else texto_parcela


def get_max_parcel_number(usufructs_in):
    return max((usu.get("parcel_number") or 0 for usu in usufructs_in), default=1)


def reordenar_numero_parcela(activity):
    from rh.dayoff.models import Usufruct
    from rh.dayoff.const import PAYMENT_FINALIZED

    query = (
        activity.acquisition_period.usufructs.exclude(
            status__in=[4096, 2048, 16, 8]  # USUFRUCT_STATUS_CHOICE
        )
        .exclude(
            ctrl_payments__payroll_ctrl_status=PAYMENT_FINALIZED,
        )
        .order_by("start_date")
    )

    cont_parcela = 1
    for usu in query:
        Usufruct.objects.filter(pk=usu.pk).update(
            numero_parcela=cont_parcela, payment_installments=query.count()
        )
        cont_parcela += 1
        q_usu_retificado_pago = usu.activity.modifieds.filter(
            ctrl_payments__payroll_ctrl_status=PAYMENT_FINALIZED
        )
        if q_usu_retificado_pago.exists():
            for usu_pago in q_usu_retificado_pago:
                Usufruct.objects.filter(pk=usu.pk).update(
                    numero_parcela=None, payment_installments=0
                )

    for usu in activity.modifieds.all():
        # Se o usufruto que foi retificado não foi pago
        if not usu.ctrl_payments.filter(payroll_ctrl_status=PAYMENT_FINALIZED).exists():
            Usufruct.objects.filter(pk=usu.pk).update(
                numero_parcela=None, payment_installments=0
            )
