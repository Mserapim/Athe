# -*- coding: utf-8 -*-
import django
import os
import json

from celery import Celery
from contrib.middleware import set_current_user
from engine.mq.models import Task
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from logging import getLogger
from rh.models import OrgaoGeral
from edocs.protocolo.models import Movimentacao

log = getLogger("tasker")

# django.setup()

app = Celery("reports")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task
def edoc_detail(
    task,
    hook,
    workplace_origin,
    workplace_destination,
    edoc_code,
    date_created,
    date_start,
    date_end,
    finalized,
    subject,
    user,
    success,
):
    state = "failed"
    message = (
        "<p>EDOC - Movimentações a partir de %s - Gerando arquivos ...</p>"
        % OrgaoGeral.objects.get(pk=(workplace_origin or workplace_destination))
    )
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        set_current_user(user)
        message = (
            "<p>EDOC - Movimentações a partir de %s - Gerando arquivos ...</p>"
            % OrgaoGeral.objects.get(pk=(workplace_origin or workplace_destination))
        )
        task.message = message
        task.state = "progress"
        task.save()

        Movimentacao.edoc_detail(
            task=task,
            workplace_origin=workplace_origin,
            workplace_destination=workplace_destination,
            edoc_code=edoc_code,
            date_created=date_created,
            date_start=date_start,
            date_end=date_end,
            finalized=finalized,
            filename="edoc_detail_%s.csv" % task.uuid,
            subject=subject,
            user=user,
            feedback=feedback,
        )

        state = "ready"
        msg_params = locals()
        msg_params.update(
            deadline=(datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y %H:%M")
        )
        msg_params.update(uuid=task.uuid)
        msg_params.update(
            mov_message="%s"
            % OrgaoGeral.objects.get(pk=(workplace_origin or workplace_destination))
        )
        message = success % msg_params
        task.data = json.dumps({"filename": "edoc_detail_%s.csv" % task.uuid})
    except Exception as err:
        log.exception(str(err))
        has_exception = err
        message = (
            "<p>EDOC - Movimentações a partir de %s - Falha na criação de arquivos.</p> <p>%s</p>"
            % (
                OrgaoGeral.objects.get(pk=(workplace_origin or workplace_destination)),
                str(err),
            )
        )

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception
