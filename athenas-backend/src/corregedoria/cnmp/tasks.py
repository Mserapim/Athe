# -*- coding: utf-8 -*-
import os
import json
import time
import django

from celery import Celery, group
from django.conf import settings
from contrib.utils import getLogger
from contrib.middleware import set_current_user
from engine.mq.models import Task
from rh.models import Servidor
from corregedoria.cnmp.workflow import ExportDataEmployee

log = getLogger("tasker")
app = Celery("celerysrdir")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task()
def export_data(task, hook):

    message = "<p>Erro ao exportar dados</p>"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:

        message = "<p>Exportando dados...</p>"
        task.message = message
        task.state = "ready"
        task.save()
        task.info(msg="Iniciando...", pct_progress=0.001)

        # Problema aqui -> Os inativos devem ser informados.
        list_of_employees = Servidor.objects.filter(ativo=True, tipo="M")

        inc_progress = 100.0 / list_of_employees.count()
        rst1 = False
        fail1 = False
        result1 = None

        job1 = group(
            [
                importing_by_employee.s(
                    membro.pk, task_father=task.uuid, inc_progress=inc_progress
                )
                for membro in list_of_employees
            ]
        )
        result1 = job1.apply_async()

        while not rst1:
            rst1 = result1.ready() if result1 else True
            time.sleep(0.5)

        fail1 = result1.failed() if result1 else False

        if not fail1:
            # state = 'ready'
            message = success
            task.finish_execution(msg=message)
        else:
            # state = 'failed'
            message = "<p>Erro ao exportar dados</p>"
            task.finish_execution(msg=message, status="ERROR")

    except Exception as err:
        log.exception(str(err))
        has_exception = err
        # state = 'failed'
        message = "<p>Erro ao exportar dados</p>"
        task.finish_execution(msg=message, status="ERROR")

    if has_exception:
        raise has_exception


@app.task()
def importing_by_employee(pk, task_father=None, inc_progress=0):
    try:
        # employee = Servidor.object.get(pk=pk)
        ExportDataEmployee.run(pk=pk)

        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info("Terminado para %s" % (pk), pct_progress=inc_progress)
    except Exception as err:
        task = Task.objects.get(uuid=task_father)
        task.info("ERROR para %s <br />%s" % (pk, err), pct_progress=inc_progress)
