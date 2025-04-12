import datetime
import decimal
import time
import os

from celery import group, Celery
from dateutil import relativedelta
from django.db import IntegrityError
from django.db.models import F, Sum
import time
import os
from contrib.daterange import NewDateRange

from contrib.utils import getLogger
from contrib.middleware import set_current_user
from engine.mq.models import Task
from rh.dayoff.const import PAYMENT_FINALIZED, USU_SOLD
from rh.dayoff.models import UsufructPaymentControl
from rh.gfp.models import Evento, ExtraPaymentPeriod, Folha
from rh.gfp.gfp_utils import get_paycheck, create_entry
from rh.gfp.vacation_payment_utils import (
    extract_base_salary_for_cms,
    get_salary_atualized,
    get_paychecks,
    calc_from_period,
    gratifications_to_check,
    calculate_average_value_of_months,
)
from standard.models import Choice


log = getLogger(__name__)
app = Celery("gratificaions_manager")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def _calculate_usufruct_payment_value(task, user, ctrl_usufruct_id, inc_progress=0):
    """
    Task para cálculo de pagamento de abono ou gratificação de férias
    """
    GRATS_CHECK_KEY = "gratifications_vacation_member"
    GRATS_SERVERS = "gratifications_vacation_servers"
    GRATS_SERVERS_MEDIA = "gratifications_vacation_servers_media"
    dict_events_number = {
        "comissioned_salary": "00600",
        "pr_comissioned_salary": "A73",
        "hard_provide": "03100",
        "pr_hard_provide": "E59",
        "diff_cne": "02400",
        "incorporate_value": "05100",
        "permanence_allowance": "05200",
        "sub-MP-FC-I": "10500",
        "valor_incorporado": "05100",
    }

    task = Task.objects.get(uuid=task)

    ctrl_usufruct = UsufructPaymentControl.objects.get(pk=ctrl_usufruct_id)

    set_current_user(user)
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    log.debug(
        f"TASK {task.uuid} - Calculando Abono / Gratificação de Férias: {ctrl_usufruct}."
    )

    try:
        calculated_value = 0
        start_date_acquisition = (
            ctrl_usufruct.usufruct.activity.acquisition_period.start_date_acquisition
        )
        end_date_acquisition = (
            ctrl_usufruct.usufruct.activity.acquisition_period.end_date_acquisition
        )

        if (
            end_date_acquisition > start_date_acquisition
            and (end_date_acquisition.day + 1) >= start_date_acquisition.day
        ):
            diff_months = (
                relativedelta.relativedelta(
                    end_date_acquisition, start_date_acquisition
                ).months
                + 1
            )
        else:
            diff_months = relativedelta.relativedelta(
                end_date_acquisition, start_date_acquisition
            ).months

        """
        Manter lógica comentada para futura consulta
        """
        # if ctrl_usufruct.employee.type_by_possession in ['EFE', 'EFC']:
        #     salary_effective = get_salary_atualized(ctrl_usufruct.employee)

        #     hard_provide_value = 0
        #     sub_MP_FC_I = None
        #     permanence_allowance = None
        #     hard_provide_months = 0
        #     for paycheck in get_paychecks(
        #         ctrl_usufruct.employee,
        #         dict_events_number.get('hard_provide', None),
        #         start_date_acquisition,
        #         end_date_acquisition
        #     ):
        #         hard_provide_value += paycheck.correct_base_value
        #         hard_provide_months += 1

        #     dt_usufruct = datetime.datetime(ctrl_usufruct.usufruct.payment_year, ctrl_usufruct.usufruct.payment_month, 1)
        #     dt_usufruct_future = dt_usufruct + relativedelta.relativedelta(months=1)

        #     epp = ExtraPaymentPeriod.objects.currents_in(
        #         range=NewDateRange(start_date_acquisition, dt_usufruct_future.date())
        #     ).filter(
        #         employee=ctrl_usufruct.employee,
        #         extra_payment__slug__startswith='ABONO-PERMANENCIA',
        #         value__gt=0
        #     ).exists()

        #     sub = ExtraPaymentPeriod.objects.currents_in(
        #         range=NewDateRange(start_date_acquisition, dt_usufruct_future.date())
        #     ).filter(
        #         employee=ctrl_usufruct.employee,
        #         extra_payment__slug__startswith='DIF-SUBMP-FC',
        #         value__gt=0
        #     ).exists()

        #     if epp:
        #         permanence_allowance = get_paychecks(
        #             ctrl_usufruct.employee,
        #             dict_events_number.get('permanence_allowance', None),
        #         ).last()

        #     if sub:
        #         sub_MP_FC_I = get_paychecks(
        #             ctrl_usufruct.employee,
        #             dict_events_number.get('sub-MP-FC-I', None),
        #         ).last()

        #     permanence_allowance_value = permanence_allowance.correct_value if permanence_allowance else 0
        #     sub_MP_FC_I_value = sub_MP_FC_I.correct_value if sub_MP_FC_I else 0

        #     event = Evento.objects.filter(numero=dict_events_number.get('incorporate_value', None),).first()

        #     incorporate_value_calc = calc_from_period(
        #         ctrl_usufruct.employee,
        #         Folha.objects.filter(tipo_folha__titulo='NORMAL').first(),
        #         event,
        #         {}
        #     )

        #     incorporate_value_calc_result = incorporate_value_calc.calculate()

        #     calculated_value = salary_effective + decimal.Decimal(incorporate_value_calc_result.get('valor_base', 0)) + ((hard_provide_value/hard_provide_months) if hard_provide_months != 0 else 0) + permanence_allowance_value + sub_MP_FC_I_value

        # if ctrl_usufruct.employee.type_by_possession in ['ECM']:
        #     salary_effective = get_salary_atualized(ctrl_usufruct.employee)

        #     dt_usufruct = datetime.datetime(ctrl_usufruct.usufruct.payment_year, ctrl_usufruct.usufruct.payment_month, 1)
        #     dt_usufruct_future = dt_usufruct + relativedelta.relativedelta(months=1)

        #     diff_cne = get_paychecks(
        #         ctrl_usufruct.employee,
        #         dict_events_number.get('diff_cne', None),
        #         dt_usufruct.date(),
        #         dt_usufruct_future.date()
        #     ).last()
        #     difference_cne_value = diff_cne.correct_value if diff_cne else 0

        #     q_incorporado = get_paychecks(
        #         ctrl_usufruct.employee,
        #         dict_events_number.get('valor_incorporado', None),
        #         start_date_acquisition,
        #         end_date_acquisition,
        #     )
        #     valor_incorporado = 0
        #     if q_incorporado.exists():
        #         total_incorporado = q_incorporado.aggregate(Sum('correct_value'))['correct_value__sum']
        #         valor_incorporado = total_incorporado / q_incorporado.count()

        #     calculated_value = salary_effective + difference_cne_value + valor_incorporado

        # if ctrl_usufruct.employee.type_by_possession in ['CMS']:

        #     salaries = extract_base_salary_for_cms(
        #         ctrl_usufruct.employee,
        #         start_date_acquisition,
        #         end_date_acquisition,
        #     )
        #     salary_effective = calculate_average_value_of_months(salaries, diff_months)
        #     hard_provide = get_paychecks(
        #         ctrl_usufruct.employee,
        #         [
        #             dict_events_number.get('hard_provide', None),
        #             dict_events_number.get('pr_hard_provide', None),
        #         ],
        #         start_date_acquisition,
        #         end_date_acquisition
        #     )
        #     try:
        #         hard_provide_value = calculate_average_value_of_months(hard_provide, diff_months)
        #         calculated_value = decimal.Decimal(salary_effective) + decimal.Decimal(hard_provide_value if hard_provide_value else 0)
        #     except Exception:
        #         calculated_value = decimal.Decimal(0)

        if ctrl_usufruct.employee.type_by_possession in ["EFE", "EFC", "ECM", "CMS"]:
            if ctrl_usufruct.employee.type_by_possession in ["CMS"]:
                salaries = extract_base_salary_for_cms(
                    ctrl_usufruct.employee,
                    start_date_acquisition,
                    end_date_acquisition,
                )
                salary_effective = calculate_average_value_of_months(
                    salaries, diff_months
                )
            else:
                salary_effective = get_salary_atualized(ctrl_usufruct.employee)

            # Somar o último valor recebido para as verbas preenchidas no parâmetro GRATS_SERVERS
            sum_gratifications = 0
            for grat in gratifications_to_check(GRATS_SERVERS):
                query = get_paychecks(ctrl_usufruct.employee, grat)

                if query.exists():
                    paycheck = query.last()
                    sum_gratifications += paycheck.correct_value

            # Calcular média dos recebimentos com base no período aquisitivo / (Quantidade de competência do período aquisitivo)
            gratification_value = 0
            for paycheck in get_paychecks(
                ctrl_usufruct.employee,
                gratifications_to_check(GRATS_SERVERS_MEDIA),
                start_date_acquisition,
                end_date_acquisition,
            ):
                gratification_value += paycheck.correct_value

            average_gratifications = gratification_value / diff_months

            calculated_value = (
                salary_effective
                + decimal.Decimal(sum_gratifications)
                + decimal.Decimal(average_gratifications)
            )

        if ctrl_usufruct.employee.type_by_possession in [
            "MBR",
            "MEL",
            "MCM",
            "MEC",
            "MBR2",
            "MEL2",
            "MCM2",
            "MEC2",
        ]:
            calculated_value = decimal.Decimal(0)

            salary_effective = get_salary_atualized(ctrl_usufruct.employee)
            gratifications_average_value = 0
            gratifications_average_months = 0
            for paycheck in get_paychecks(
                ctrl_usufruct.employee,
                gratifications_to_check(GRATS_CHECK_KEY),
                start_date_acquisition,
                end_date_acquisition,
            ):
                gratifications_average_value += paycheck.correct_value
                gratifications_average_months += 1

            dt_usufruct = datetime.datetime(
                ctrl_usufruct.usufruct.payment_year,
                ctrl_usufruct.usufruct.payment_month,
                1,
            )
            dt_usufruct_future = dt_usufruct + relativedelta.relativedelta(months=1)

            q_epp = ExtraPaymentPeriod.objects.currents_in(
                range=NewDateRange(start_date_acquisition, dt_usufruct_future.date())
            ).filter(
                employee=ctrl_usufruct.employee,
                extra_payment__slug__startswith="ABONO-PERMANENCIA",
                value__gt=0,
            )

            permanence_allowance_value = 0
            if q_epp.exists():
                epp = q_epp.first()
                permanence_allowance = get_paychecks(
                    ctrl_usufruct.employee,
                    dict_events_number.get("permanence_allowance", None),
                    start_date_acquisition=epp.start_validity,
                    end_date_acquisition=epp.end_validity,
                ).last()
                permanence_allowance_value = permanence_allowance.correct_value

            gratifications_vacation = gratifications_average_value / diff_months
            calculated_value = (
                decimal.Decimal(salary_effective)
                + decimal.Decimal(permanence_allowance_value)
                + decimal.Decimal(gratifications_vacation)
            )

            # Adicional de férias, apenas para membros
            if ctrl_usufruct.usufruct.status == USU_SOLD:
                calculated_value *= 2

            calculated_value = (
                calculated_value / ctrl_usufruct.usufruct.payment_installments
            )

        if ctrl_usufruct.usufruct.status == USU_SOLD:
            calculated_value = (
                calculated_value / 30 * 2 * int(ctrl_usufruct.usufruct.days)
            )
        ctrl_usufruct.calculated_value = decimal.Decimal(
            str(round(calculated_value, 3))[:-1]
        )
        ctrl_usufruct.save()
        message = f"<p>Cálculo do valor previsto do usufruto {ctrl_usufruct} concluído."
        task.info(msg=message, pct_progress=decimal.Decimal(inc_progress))
        task.save()

    except Exception as err:
        log.exception(err)
        message = f"<p>Erro ao calcular o valor previsto para {ctrl_usufruct}</p>"
        task.info(msg=message, type_of=3, pct_progress=decimal.Decimal(inc_progress))
        task.save()
    if task:
        Task.objects.filter(uuid=task).update(progress=F("progress") + inc_progress)


@app.task()
def _implement_usufruct_payment_value(
    task_uuid, user, ctrl_usufruct_id, payroll_id, inc_progress=0
):
    """
    Task para implementar em folha as gratificações e abonos
    """
    try:
        task = Task.objects.get(uuid=task_uuid)
        ctrl_usufruct = UsufructPaymentControl.objects.filter(
            id=ctrl_usufruct_id
        ).first()
        if ctrl_usufruct:
            payroll_to_apply = Folha.objects.get(pk=payroll_id)
            set_current_user(user)
            status = ""
            installments = (
                ctrl_usufruct.payment_installments
                if ctrl_usufruct.payment_installments
                else 1
            )
            if ctrl_usufruct.usufruct.status == USU_SOLD:
                status = "Venda"
                event_to_apply = Evento.objects.get(numero="05600")
                if ctrl_usufruct.employee.is_member:
                    installments = Choice.objects.get(
                        app_label="gfp", name="GFP_INSTALLMENTS_MEMBER_VACATION"
                    ).value
            else:
                status = "Usufruto"
                event_to_apply = Evento.objects.get(numero="05000")
            paycheck_to_apply = get_paycheck(ctrl_usufruct.employee, payroll_to_apply)
            create_entry(
                paycheck_to_apply,
                event_to_apply,
                qtd=ctrl_usufruct.usufruct.days,
                qtd_max=ctrl_usufruct.usufruct.activity.acquisition_period.days,
                installments_paid=1,
                installments=installments,
                base_value=ctrl_usufruct.confirmed_value,
                value=ctrl_usufruct.confirmed_value / installments,
                contribution_base=ctrl_usufruct.confirmed_value / installments,
                info=f"{ctrl_usufruct} | {status} | {ctrl_usufruct.usufruct.activity.acquisition_period.group_period}",
                insertion_type=7,  # Choice id 7 - Tipo de Inserção: Gestor de Férias
            )
            ctrl_usufruct.payroll_ctrl_status = PAYMENT_FINALIZED
            ctrl_usufruct.paid_value = ctrl_usufruct.confirmed_value
            ctrl_usufruct.save()
        if task:
            Task.objects.filter(uuid=task_uuid).update(
                progress=F("progress") + inc_progress
            )

    except Exception as err:
        log.exception(err)
        if task:
            task = Task.objects.get(uuid=task)
            task.info(msg=f"Erro implentado ferias/abono {err}", type_of=3)


@app.task()
def start_implement_usufruct_payment(
    task, hook, user_pk, control_usufructs, payroll_id
):
    task = Task.objects.get(uuid=task)
    message = f"<p>Implementação de Abono/Gratificação em folha.</p>"
    task.message = message
    task.state = "progress"
    task.save()
    control_usufructs = UsufructPaymentControl.objects.filter(pk__in=control_usufructs)

    total = control_usufructs.count()

    inc_progress = 100.0 / total if total else 0
    result = None
    job = group(
        [
            _implement_usufruct_payment_value.s(
                task.uuid,
                user=user_pk,
                ctrl_usufruct_id=ctrl_usufruct.pk,
                payroll_id=payroll_id,
                inc_progress=inc_progress,
            )
            for ctrl_usufruct in control_usufructs
        ]
    )

    result = job.apply_async(queue="important")

    while not result.ready():
        time.sleep(2)

    task.info(pct_progress=100)
    task.finish_execution()


@app.task()
def start_calculate_usufruct_payment(task, hook, user_pk, control_usufructs):
    task = Task.objects.get(uuid=task)
    message = f"<p>Calculando Pagamento de Férias.</p>"
    task.message = message
    task.state = "progress"
    task.save()

    control_usufructs = UsufructPaymentControl.objects.filter(pk__in=control_usufructs)
    total = control_usufructs.count()

    inc_progress = 100.0 / total if total else 0
    result = None

    job = group(
        [
            _calculate_usufruct_payment_value.s(
                task.uuid,
                user=user_pk,
                ctrl_usufruct_id=ctrl_usufruct.pk,
                inc_progress=inc_progress,
            )
            for ctrl_usufruct in control_usufructs
        ]
    )

    result = job.apply_async(queue="important")

    while not result.ready():
        time.sleep(2)

    task.info(pct_progress=100)
    task.finish_execution()
