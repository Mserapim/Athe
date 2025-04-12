import time
import os

from celery import Celery
from contrib.utils import getLogger
from contrib.middleware import set_current_user

from django.db.models import F
from engine.mq.models import Task

from standard.models import Choice
from rh.defin.models import PFProviderEntry
from rh.gfp.models import Folha as Payroll, Evento as Event

from rh.gfp.gfp_utils import get_paycheck, create_entry
from rh.gfp.paycheckdifference_utils import *

log = getLogger(__name__)
app = Celery("gfp")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def applicate_eventual_provider_task(task, hook, user, entry_id, payroll_id):
    """
    Esta Task é responsável por aplicar os lançamentos de Prestadores Eventuais na Folha
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
    provider_entry = PFProviderEntry.objects.get(pk=entry_id)

    set_current_user(user)
    feedback(
        "",
        0,
        message=f"<p>Aplicando lançamento de Prestador Eventual: {provider_entry}</p>",
        state=state,
    )
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    log.debug(
        f"TASK {task.uuid} - Aplicando lançamento de Prestador Eventual: {provider_entry}."
    )

    try:
        payroll_to_apply = Payroll.objects.get(pk=payroll_id)
        event_to_apply = Event.objects.get(numero="60000")
        employee = provider_entry.natural_person.servidor_set.filter(
            type_by_possession="COE"
        ).first()
        paycheck_to_apply = get_paycheck(employee, payroll_to_apply)

        create_entry(
            paycheck_to_apply,
            event_to_apply,
            qtd_max=1,
            pct=0,
            value=provider_entry.gross_value,
            base_value=provider_entry.gross_value,
            info=f"{provider_entry.pay_day}",
            ref_year=provider_entry.pay_day.year,
            ref_month=provider_entry.pay_day.month,
            insertion_type=6,  # Choice id 6 - Tipo de Inserção: Gestor de Prestador Eventual
        )
        provider_entry.applied_payroll = True
        provider_entry.save()

        state = "ready"
        message = f"<p>Aplicação concluída do lançamento de Prestador Eventual: {provider_entry}."
    except Exception as err:
        log.exception(err)
        state = "failed"
        message = f"<p>Erro ao aplicar o lançamento de Prestador Eventual: {provider_entry}</p>"
        task.info(
            msg=f"<p>Erro ao aplicar o lançamento de Prestador Eventual: {provider_entry}</p>",
            type_of=3,
        )

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()
