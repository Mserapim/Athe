import json
import os
from datetime import datetime, timedelta
from logging import getLogger

from celery import Celery

from contrib.middleware import set_current_user
from engine.mq.models import Task
from rh.generators.cnmp_report import CNMPReport

log = getLogger("tasker")

app = Celery("cnpmreport")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task
def cnmp_report_maker(task, hook, user, success):
    state = "failed"
    message = "<p>RH - Gerando relatório CNMP ...</p>"
    task = Task.objects.get(uuid=task)

    print("cnmp_report_task")

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    try:
        set_current_user(user)
        message = f"<p>RH - Relatório CNMP - Gerando arquivos ...</p>"
        task.message = message
        task.state = "progress"
        task.save()

        cnmp = CNMPReport(feedback=feedback, task=task)
        cnmp.generate()
        state = "ready"
        msg_params = locals()
        msg_params.update(
            deadline=(datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y %H:%M")
        )
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        task.data = json.dumps(
            {
                "filename": cnmp.filename,
                "file_path": cnmp.file_path,
            }
        )

    except Exception as err:
        log.exception(err)
        message = "<p>RH - Relatório CNMP - Falha na criação de arquivos.</p>"

    task.message = message
    task.state = state
    task.save()
