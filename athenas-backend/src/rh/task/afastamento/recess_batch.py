# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timedelta
from logging import getLogger

from celery import Celery

from contrib.middleware import set_current_user
from engine.mq.models import Task
from rh.afastamento.models import BaseLicencaAfastamento

log = getLogger(__name__)

app = Celery("createbatchrecess")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task()
def create_batch_recess_task(
    task,
    hook,
    start_date,
    end_date,
    employee_type,
    insert_registry,
    exclude_registry,
    user,
    success,
):
    state = "failed"
    message = "<p>RH - Criando recesso para os servidores...</p>"
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

        BaseLicencaAfastamento.create_batch_recess(
            start_date=start_date,
            end_date=end_date,
            employee_type=employee_type,
            insert_registry=insert_registry,
            exclude_registry=exclude_registry,
            user=user,
            task=task,
        )

        state = "ready"
        msg_params = locals()
        msg_params.update(
            deadline=(datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y %H:%M")
        )
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        data = datetime.today()
        filename = "demonstrativo_recessos_%s.txt" % (
            datetime.strftime(data, "%d_%m_%Y_%H_%M")
        )
        task.data = json.dumps({"filename": filename})

    except Exception as err:
        has_exception = err
        message = (
            "<p>RH - Criando recesso para os servidores. Falha na criação dos recessos.</p><p>%s</p>"
            % err
        )

    feedback("", 100)
    task.message = message
    task.state = state
    task.save()
    task.finish_execution()

    if has_exception:
        raise has_exception
