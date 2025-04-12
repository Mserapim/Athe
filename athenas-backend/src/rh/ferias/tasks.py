# -*- coding: utf-8 -*-
import os
from logging import getLogger

from celery import Celery
from datetime import datetime

from contrib.middleware import set_current_user
from engine.mq.models import Task
from dateutil.relativedelta import relativedelta
from rh.ferias.models import PeriodoAquisitivoServidor, PeriodoAquisitivo

log = getLogger(__name__)

app = Celery("ferias")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task()
def create_automatic_book_vacation(task, hook, pa, type_employee, success, user):
    state = "failed"
    message = "<p>FÉRIAS - Marcando férias...</p>"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        set_current_user(user)

        task.message = message
        task.state = "progress"
        task.save()

        PeriodoAquisitivoServidor._create_automatic_book_vacation(
            pa=pa, type_employee=type_employee, user=user, task=task.pk
        )

        message = "<p>FÉRIAS - Marcando férias finalizado.</p>"

        deadline = (datetime.now().date() + relativedelta(days=2)).strftime("%d/%m/%Y")
        msg_params = locals()
        msg_params.update(deadline=deadline)
        msg_params.update(uuid=task.uuid)
        message = success % msg_params

        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = (
            "<p>FÉRIAS - Marcando férias. Falha na criação de arquivos.</p><p>%s</p>"
            % err
        )

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def homologate(task, hook, pa, publication, force, user, success):
    state = "failed"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        set_current_user(user)

        pa = PeriodoAquisitivo.objects.get(pk=pa)
        task.message = "<p>FÉRIAS - Homologando %s férias...</p>" % pa
        task.state = "progress"
        task.save()

        pa.homologate(publication=publication, force=force, task=task)

        deadline = (datetime.now().date() + relativedelta(days=2)).strftime("%d/%m/%Y")
        msg_params = locals()
        msg_params.update(deadline=deadline)
        msg_params.update(uuid=task.uuid)
        message = success % msg_params

        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = (
            "<p>FÉRIAS - Homologando %s férias. Falha na homologação de arquivos.</p><p>%s</p>"
            % (pa, err)
        )

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception
