import time
import os
from celery import Celery, group
from contrib.utils import getLogger
from contrib.middleware import set_current_user
from django.db.models import F
from engine.mq.models import Task
from rh.models import Servidor as Employee
from rh.gfp.models import (
    Folha,
    FolhaEvento,
    ConferencePayroll,
    ConferenceEventPayroll,
    Evento,
)


log = getLogger(__name__)
app = Celery("gfp")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def process_check_payroll(task, hook, payroll_id=None, conference_id=None, user=None):
    set_current_user(user)
    conference = ConferencePayroll.objects.get(pk=conference_id)
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        task.message = f"<p>Processando conferência de Folha {conference.payroll}.</p>"
        task.state = "progress"
        task.progress = 0
        task.save()

        payroll = conference.payroll
        payroll_entrie_automated = FolhaEvento.objects.filter(
            folha__pk=payroll_id, automated=True
        )
        payroll_entrie_manual = FolhaEvento.objects.filter(
            folha__pk=payroll_id, automated=False
        )
        month = 12 if payroll.periodo.mes == 1 else payroll.periodo.mes - 1
        year = (
            payroll.periodo.ano - 1 if payroll.periodo.mes == 1 else payroll.periodo.ano
        )

        list_objects = []

        for entrie in payroll_entrie_automated:
            check = False
            entrie_previous = entrie.copia_de
            if entrie_previous:
                if entrie.correct_value == entrie_previous.correct_value:
                    check = True
            obj = ConferenceEventPayroll(
                conference=conference,
                event_payroll_previous=entrie_previous,
                event_payroll_current=entrie,
                event_paycheck_previous=(
                    entrie_previous.contracheque if entrie_previous else None
                ),
                event_paycheck_current=entrie.contracheque,
                checked=check,
            )
            list_objects.append(obj)

        for entrie in payroll_entrie_manual:
            check = False
            month_previous = month
            year_previous = year
            entrie_previous = FolhaEvento.objects.filter(
                reference_month=month_previous,
                reference_year=year_previous,
                evento=entrie.evento,
                correct_value=entrie.correct_value,
                contracheque__folha__tipo_folha=entrie.contracheque.folha.tipo_folha,
                servidor=entrie.servidor,
            ).first()

            if entrie_previous:
                if entrie.correct_value == entrie_previous.correct_value:
                    check = True
            obj = ConferenceEventPayroll(
                conference=conference,
                event_payroll_previous=entrie_previous,
                event_payroll_current=entrie,
                event_paycheck_previous=(
                    entrie_previous.contracheque if entrie_previous else None
                ),
                event_paycheck_current=entrie.contracheque,
                checked=check,
            )
            list_objects.append(obj)

        ConferenceEventPayroll.objects.bulk_create(list_objects)

        if payroll.folha_anterior:
            payroll_previous = payroll.folha_anterior
            payroll_entrie_previuos = FolhaEvento.objects.filter(
                folha__pk=payroll_previous.pk,
                conference_event_payroll_previous__isnull=True,
            ).distinct()
            list_objects_previous = []
            for entrie in payroll_entrie_previuos:
                obj = ConferenceEventPayroll(
                    conference=conference,
                    event_payroll_previous=entrie,
                    event_paycheck_previous=entrie.contracheque,
                    event_paycheck_current=entrie.contracheque.next_paycheck,
                    checked=False,
                )
                list_objects_previous.append(obj)

            ConferenceEventPayroll.objects.bulk_create(list_objects_previous)

        task.finish_execution()
    except Exception as err:
        log.exception(err)
        has_exception = err
        task.info(msg=f"Erro em {err}", type_of=3)
        task.finish_execution(status="ERROR")

    if has_exception:
        raise has_exception


@app.task()
def delete_entries_task(task, hook, user, payroll_id, event_id):
    """
    Esta Task é responsável por deletar os lançamentos de uma verba e folha selecionadas
    Sendo que a verba não pode estar lançada como automática
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
    payroll = Folha.objects.get(pk=payroll_id)
    event = Evento.objects.get(pk=event_id)
    entries_ids = FolhaEvento.objects.filter(
        folha=payroll_id, evento=event_id, automated=False
    ).values_list("pk", flat=True)
    message = f"<p>Erro ao deletar os lançamentos: Verba {event} - Folha {payroll}</p>"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback(
        "",
        0,
        message=f"<p>Deletando lançamentos: Verba {event} - Folha {payroll}</p>",
        state=state,
    )
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        try:
            inc_progress = 100.0 / len(entries_ids)
        except ZeroDivisionError:
            inc_progress = 1

        group_job = []
        for entry_id in entries_ids:
            group_job.append(
                delete_entry.s(task.uuid, inc_progress, entry_id, event_id, payroll_id)
            )

        result = None
        job = group(group_job)

        result = job.apply_async()
        while not result.ready():
            time.sleep(2)

        state = "ready"
        message = (
            f"<p>Concluído - Lançamentos deletados: Verba {event} - Folha {payroll}."
        )
    except Exception as err:
        log.exception(err)
        state = "failed"
        message = (
            f"<p>Erro ao deletar os lançamentos: Verba {event} - Folha {payroll}</p>"
        )
        task.info(
            msg=f"<p>Erro ao deletar os lançamentos: Verba {event} - Folha {payroll}</p>",
            type_of=3,
        )

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def delete_entry(task_uuid, inc_progress, entry_id, event_id, payroll_id):
    task = Task.objects.get(uuid=task_uuid) if task_uuid else None

    entry = FolhaEvento.objects.get(pk=entry_id)
    payroll = Folha.objects.get(pk=payroll_id)
    event = Evento.objects.get(pk=event_id)
    try:
        entry.delete()
        entry.contracheque.recalculate()
    except Exception as e:
        if task:
            task.info(msg=f"Erro {e} ao deletar {event}, da {payroll}", type_of=3)

    if task:
        Task.objects.filter(pk=task.pk).update(progress=F("progress") + inc_progress)
