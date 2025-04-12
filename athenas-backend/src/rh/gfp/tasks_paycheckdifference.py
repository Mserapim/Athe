import time
import os

from celery import Celery, group
from contrib.utils import getLogger
from contrib.middleware import set_current_user

from django.db.models import F
from engine.mq.models import Task

from rh.models import Servidor as Employee
from rh.gfp.models import (
    Folha as Payroll,
    ContraCheque as Paycheck,
    Evento as Event,
    PeriodPayroll,
    DifferencePayroll,
)

from rh.gfp.gfp_utils import get_paycheck, create_entry
from rh.gfp.paycheckdifference_utils import *

log = getLogger(__name__)
app = Celery("gfp")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def calculate_period_task(task, hook, user, period_id):
    """
    Esta Task é responsável por calcular a diferença de folha de um período selecionado
    """
    period = PeriodPayroll.objects.get(pk=period_id)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    state = "progress"
    employees_ids = get_employees_to_compare()
    events_ids = get_events_to_compare(period)
    message = f"<p>Erro ao calcular o período: {period}</p>"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback("", 0, message=f"<p>Cálculo do período {period}</p>", state=state)
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    log.debug(f"TASK {task.uuid} - Calculando o período: {period}.")
    log.debug(f"TASK {task.uuid} - Total employees: {len(employees_ids)}.")
    try:
        try:
            inc_progress = 100.0 / len(employees_ids)
        except ZeroDivisionError:
            inc_progress = 1

        clean_differences()

        group_job = []
        for employee_id in employees_ids:
            employee = Employee.objects.get(pk=employee_id)

            paychecks_ids = [
                pc.pk
                for pc in employee.paychecks.filter(
                    folha__periodo__mes=period.folha.periodo.mes,
                    folha__periodo__ano=period.folha.periodo.ano,
                )
            ]
            log.debug(f"TASK {task.uuid} - Paychecks: {paychecks_ids}")

            group_job.append(
                check_differences.s(
                    task.uuid,
                    inc_progress,
                    employee_id,
                    period_id,
                    paychecks_ids,
                    events_ids,
                )
            )

        result = None
        job = group(group_job)

        result = job.apply_async()
        while not result.ready():
            time.sleep(2)

        state = "ready"
        message = f"<p>Cálculo do período {period} concluído."
    except Exception as err:
        log.exception(err)
        state = "failed"
        message = f"<p>Erro ao calcular período {period}</p>"
        task.info(msg=f"<p>Erro ao calcular período {period}</p>", type_of=3)
    log.debug(f"TASK FINALIZADA")

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def check_differences(
    task_uuid, inc_progress, employee_id, period_id, paychecks_ids, events_ids
):
    task = Task.objects.get(uuid=task_uuid) if task_uuid else None

    employee = Employee.objects.get(pk=employee_id)
    period = PeriodPayroll.objects.get(pk=period_id)
    log.debug(f"emp {employee}")
    log.debug(f"period {period}")
    try:
        log.debug(f"events {Event.objects.filter(pk__in=events_ids)}")
        for event in Event.objects.filter(pk__in=events_ids):
            entry = get_entry(event, paychecks_ids)
            payroll = get_payroll(entry, period)
            values_calc = calc_from_period(employee, payroll, event)

            if event.numero == ["70100"] or (
                event.numero in ["00100", "00600"]
                and values_calc["valor"] == 0
                and len(values_calc["choices"]) > 1
            ):
                for choice in values_calc["choices"]:
                    params = {"oIds": [choice[0]]}
                    values_calc_with_params = calc_from_period(
                        employee, payroll, event, params
                    )
                    entry_from_choice = get_entry_from_choices(choice[0], payroll)

                    check_and_create_difference(
                        employee,
                        period,
                        event,
                        entry_from_choice,
                        values_calc_with_params,
                    )
            else:
                check_and_create_difference(employee, period, event, entry, values_calc)
    except Exception as e:
        if task:
            task.info(
                msg=f"Erro {e} ao calcular diferença do período {period}, do servidor {employee}",
                type_of=3,
            )

    if task:
        Task.objects.filter(pk=task.pk).update(progress=F("progress") + inc_progress)


@app.task()
def applicate_difference_task(task, hook, user, difference_id, payroll_id):
    """
    Esta Task é responsável por aplicar a diferença de folha
    """

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    state = "progress"
    task = Task.objects.get(uuid=task)

    diff_payroll = DifferencePayroll.objects.get(pk=difference_id)

    set_current_user(user)
    feedback("", 0, message=f"<p>Aplicando diferença: {diff_payroll}</p>", state=state)
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    log.debug(f"TASK {task.uuid} - Aplicando diferença: {diff_payroll}.")

    try:
        payroll_to_apply = Payroll.objects.get(pk=payroll_id)

        genre_number = diff_payroll.event.genre_event.genre_number
        specie_number = "01" if diff_payroll.type_diff == "PROV" else "02"
        event_to_apply = get_event_to_apply(genre_number, specie_number)

        paycheck_to_apply = get_paycheck(diff_payroll.employee, payroll_to_apply)

        # create_entry_from_difference(paycheck_to_apply, diff_payroll, event_to_apply)
        if diff_payroll.period.folha:
            ref_year = diff_payroll.period.folha.periodo.ano
            ref_month = diff_payroll.period.folha.periodo.mes
            info = f"{ref_month}/{ref_year}"
        else:
            ref_year = diff_payroll.period.year
            ref_month = diff_payroll.period.month
            info = f"{diff_payroll.period.month}/{diff_payroll.period.year}"
        create_entry(
            paycheck_to_apply,
            event_to_apply,
            qtd=diff_payroll.qtd_diff,
            qtd_max=diff_payroll.qtd_max_diff,
            installments_paid=diff_payroll.installment_paid_diff,
            installments=diff_payroll.installments_diff,
            pct=diff_payroll.pct_event_diff,
            value=diff_payroll.value_diff,
            base_value=diff_payroll.base_value_diff,
            employer_value=diff_payroll.employer_value_diff,
            info=info,
            ref_year=ref_year,
            ref_month=ref_month,
            contribution_base=diff_payroll.contribution_base_diff,
            insertion_type=4,  # Choice id 4 - Tipo de Inserção: Gestor de Diferenças
        )
        update_diff_payroll_to_applied(paycheck_to_apply, diff_payroll, event_to_apply)

        state = "ready"
        message = f"<p>Aplicação concluída da diferença: {diff_payroll}."
    except Exception as err:
        log.exception(err)
        state = "failed"
        message = f"<p>Erro ao aplicar a diferença: {diff_payroll}</p>"
        task.info(msg=f"<p>Erro ao aplicar a diferença: {diff_payroll}</p>", type_of=3)

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()
