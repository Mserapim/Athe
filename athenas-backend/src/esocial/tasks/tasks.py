# -*- coding: utf-8 -*-
import os
import time

from celery import Celery, group
from celery.exceptions import MaxRetriesExceededError
from django.db.models import Count

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from engine.mq.models import Task
from esocial.const import PROCESS_STATUS_EVENT_VALIDS_SENT
from esocial.extractors.base import task_info, update_task
from esocial.models import BatchEvent, Event

log = getLogger("esocial")
app = Celery("esocial")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))

app.conf.update(worker_pool_restarts=True)

MAX_RETRY_CONSULT = 50


@app.task()
def create_batches(task_father, progress, user):
    message = "<p>Criando lotes (e-Social)</p>"
    task = Task.objects.get(uuid=task_father)
    set_current_user(user)

    has_exception = None
    try:
        BatchEvent.create_batches(generate_xml=True, task=task)
        # print(groups)
        # total_batches = 0
        # for k in groups:
        #     total_batches += len(groups[k] or [])
        # task.info(f'Lotes criados: {total_batches}')
    except Exception as err:
        log.exception("{}".format(err))
        has_exception = err
        message = "Erro ao criar lotes"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
    if has_exception:
        raise has_exception


@app.task
def send_batch(task_father, batch, progress, user):
    set_current_user(user)
    task_father = Task.objects.get(uuid=task_father)
    batch = BatchEvent.objects.get(pk=batch)
    try:
        batch.send_to_esocial()
    except Exception as err:
        message = "Erro com o lote: %s" % batch.pk
        task_father.info("%s<br />%s" % (message, err), type_of=3)
    else:
        task_father.info(
            "Lote %s enviado." % batch.pk, type_of=1, pct_progress=progress
        )


@app.task()
def consult_batch(task_father, batch, progress, user):
    set_current_user(user)
    task_father = Task.objects.get(uuid=task_father)
    batch = BatchEvent.objects.get(pk=batch)
    task_father.info("Consultando lote %s..." % batch.pk, type_of=1)
    result = batch.consult_process(True, task=task_father)
    if result:
        task_father.info(
            "Lote %s processado com sucesso!" % batch.pk,
            type_of=1,
            pct_progress=progress * batch.events.count(),
        )


@app.task()
def send_batches(task_father, user, progress):
    task_father = Task.objects.get(uuid=task_father)
    message = "<p>Enviando/Consultando lotes (e-Social)</p>"
    task_father.message = message
    task_father.state = "progress"
    task_father.progress = 0
    task_father.save()

    batches_to_send = BatchEvent.objects.filter(delivery_status=2)
    if batches_to_send.exists():
        # Verificando se existe lotes do grupo 1, pois caso haja, necessita ser enviado um por um,
        # ou seja, só posso enviar o próximo quando o ultimo estiver sido processado
        batches_g1 = batches_to_send.filter(group=1)
        if batches_g1.exists():
            # Se tiver lotes do grupo 1, query recebe apenas 1 deles
            batches_to_send = batches_g1[0:1]

        job = group(
            [
                send_batch.s(
                    task_father=task_father.uuid,
                    batch=batch.pk,
                    progress=progress,
                    user=user,
                )
                for batch in batches_to_send
            ]
        )
        # result = job.apply_async(queue='low-priority')
        # result = job.apply_async()
        result = job.apply_async(queue="esocial-events")

        while not result.ready():
            log.debug(
                f"send_batches result.completed_count() {result.completed_count()}"
            )
            time.sleep(1)

        message = "<p>Lotes <b>%s</b> - enviados!</p>" % [b.pk for b in batches_to_send]
        task_father.info(
            msg="Envios finalizados - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
            type_of=1,
            pct_progress=50,
        )


@app.task(bind=True, max_retries=30)
def consult_batches(self, task_father, user, progress):
    task_father = Task.objects.get(uuid=task_father)
    batches_to_consult = BatchEvent.objects.filter(process_status=101).exclude(
        delivery_status__in=[1, 2]
    )
    if batches_to_consult.exists():
        job = group(
            [
                consult_batch.s(
                    task_father=task_father.uuid,
                    batch=batch.pk,
                    progress=progress,
                    user=user,
                )
                for batch in batches_to_consult
            ]
        )
        # result = job.apply_async(queue='low-priority')
        # result = job.apply_async()
        result = job.apply_async(queue="esocial-events")

        while not result.ready():
            log.debug(
                f"consult_batches result.completed_count() {result.completed_count()}"
            )
            time.sleep(1)

        # message = '<p>A(s) consulta(s) do(s) lote(s) <b>%s</b> foi concluída!</p>' % [b.pk for b in batches_to_consult]
        # task_father.info(msg=message, type_of=1, pct_progress=50)
        no_response_batches = BatchEvent.objects.filter(process_status=101).exclude(
            delivery_status__in=[1, 2]
        )
        if no_response_batches.exists():
            # cuttoff = no_response_batches.count() * iprogress
            # task_father.increment_progress(-cuttoff)
            try:
                self.retry(countdown=5)
            except MaxRetriesExceededError:
                log.debug("NAO TERMINOU a TEMPO")
                raise Exception("Numero maximo de tentativas excedido!")


def _create_batches(task):
    message = "<p>Criando lotes (e-Social)</p>"

    try:
        BatchEvent.create_batches(generate_xml=True, task=task)
    except Exception as err:
        log.exception("{}".format(err))
        message = "Erro ao criar lotes"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)


def _send_batches(task):
    """Este método faz o envio dos lotes já criados caso existam lotes
    não enviados e não haja lote do grupo 1 aguardando processamento.

    Args:
        task (Task): Task responsável por notificar o andamento na tarefa
        progress (float): Valor a ser incrementado por cada evento processado
        user (_type_): _description_
    """ """"""

    progress_message = "Eviando lotes - "

    batches_to_send = BatchEvent.objects.filter(delivery_status=2)
    batches_to_process = BatchEvent.objects.filter(
        delivery_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT, process_status=101
    )
    if batches_to_send.exists() and not batches_to_process.filter(group=1).exists():
        # Verificando se existe lotes do grupo 1, pois caso haja, necessita ser enviado um por um,
        # ou seja, só posso enviar o próximo quando o ultimo estiver sido processado
        batches_send_g1 = batches_to_send.filter(group=1)
        if batches_send_g1.exists():
            # Se tiver lotes do grupo 1, query recebe apenas 1 deles
            batches_to_send = batches_send_g1[0:1]

        total = batches_to_send.count()
        Task.objects.filter(uuid=task.uuid).update(progress=0)
        task.refresh_from_db()
        for batch in batches_to_send:

            try:
                time.sleep(1)
                batch.send_to_esocial()
                update_task(progress_message=progress_message, task=task, total=total)
            except Exception as err:
                message = "Erro com o lote: %s" % batch.pk
                task.info("%s<br />%s" % (message, err), type_of=3)
            else:
                task.info("Lote %s enviado." % batch.pk, type_of=1)


def _consult_batches(task, progress):
    progress_message = "Consultando lotes - "
    retry = 1
    batches_to_consult = BatchEvent.objects.filter(
        delivery_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT, process_status=101
    )
    while batches_to_consult.exists() and retry <= MAX_RETRY_CONSULT:
        total = batches_to_consult.count()
        Task.objects.filter(uuid=task.uuid).update(progress=0)
        task.refresh_from_db()
        for batch in batches_to_consult.order_by("delivery_date"):
            time.sleep(1)
            task.info(f"Consultando lote {batch.pk}... ({retry})", type_of=1)
            result = batch.consult_process(True, task=task)
            if result:
                task.info(
                    "Lote %s processado com sucesso!" % batch.pk,
                    type_of=1,
                    pct_progress=progress * batch.events.count(),
                )
            update_task(progress_message=progress_message, task=task, total=total)

        # message = '<p>A(s) consulta(s) do(s) lote(s) <b>%s</b> foi concluída!</p>' % [b.pk for b in batches_to_consult]
        # task.info(msg=message, type_of=1, pct_progress=50)
        batches_to_consult = BatchEvent.objects.filter(
            delivery_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT, process_status=101
        )
        retry += 1


@app.task()
def process_batches2(task, hook, user):
    message = "<p>Processando lotes (e-Social)</p>"
    task = Task.objects.get(uuid=task)
    final_state = "SUCCESS"
    msg = "Iniciando..."
    task.state = "ready"
    task.message = message
    task.progress = 0
    task.save()

    task.info(msg, pct_progress=0)
    all_to_process = (
        BatchEvent.objects.filter(process_status=101).exclude(delivery_status=1).count()
        * 0.5
    )
    try:
        log.debug(all_to_process)
        args = {"task_father": task.uuid, "user": user, "progress": all_to_process}
        sends = send_batches.apply_async(kwargs=args)
        log.debug(sends)
        while not sends.ready():
            time.sleep(1)
        consults = consult_batches.apply_async(kwargs=args)
        log.debug(sends)
        while not consults.ready():
            time.sleep(1)
        # if consults.state == 'failed':
        #     raise Exception('Quantidade máxima de tentativas de consulta excedidas')
        msg = "Processamento finalizado em - %s" % time.strftime("%d/%m/%Y %H:%M:%S")
    except Exception as err:
        log.exception(err)
        msg = "Erro %s" % err
        final_state = "failed"
    task.finish_execution(msg=msg, status=final_state)


@app.task()
def process_batches(task, hook, user):
    set_current_user(user)
    message = "<p>Criação, envio e processamento de lotes (e-Social)</p>"
    task = Task.objects.get(uuid=task)
    final_state = "SUCCESS"
    msg = "Iniciando..."
    # task.state = 'ready'
    task.state = "progress"
    task.description = "<p>Criação, envio e processamento de lotes (e-Social)</p>"
    task.message = message
    task.progress = 0
    task.save()

    task.info(msg, pct_progress=0)

    def events_to_process():
        q_events = Event.objects.filter(process_status__in=[1, 2, 3, 4], internal=False)
        total_events = q_events.count()
        group_events = (
            q_events.order_by("process_status")
            .values("process_status")
            .annotate(Count("process_status"))
        )
        dict_events = {
            ge["process_status"]: ge["process_status__count"] for ge in group_events
        }
        return total_events, dict_events

    total_events, control_events = events_to_process()
    aux_control = {}
    cycles = 1
    pct_progress = 1.0 / (total_events or 1) * 100
    msg = "Nenhum evento foi encontrado para ser enviado!"

    try:
        while total_events > 0 and control_events != aux_control:
            task_info(task, f"Ciclo de processamento {cycles:03d}...")
            cycles += 1
            aux_control = control_events

            # Realizar a criação dos lote, caso tenha eventos para serem empacotados
            _create_batches(task)

            # Realizar o envio dos lotes, caso tenha lotes para serem enviados
            _send_batches(task)

            # Realizar a consulta dos lotes enviados, caso tenha lotes para serem consultados
            _consult_batches(task, pct_progress)

            total_events, control_events = events_to_process()
            if aux_control == control_events:
                task_info(
                    task,
                    f"Processamemto será finalizado por não haver alteração dos status dos eventos. {aux_control}",
                )

        msg = "Processamento finalizado em - %s" % time.strftime("%d/%m/%Y %H:%M:%S")

    except Exception as err:
        log.exception(err)
        msg = "Erro %s" % err
        final_state = "failed"
    task.finish_execution(msg=msg, status=final_state)
