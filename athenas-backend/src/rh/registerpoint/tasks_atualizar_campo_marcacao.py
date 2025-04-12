import time
import os
from datetime import datetime

from celery import Celery
from contrib.utils import getLogger
from contrib.middleware import set_current_user

from engine.mq.models import Task

from rh.registerpoint.models import MarkPoint

log = getLogger(__name__)
app = Celery("gfp")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def atualizar_campo_marcacao_task(task, hook, user, marcacao_id):
    """
    Esta Task é responsável por atualizar o campo marcacao do model MarkPoint
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
    msg = f"<p>Erro ao atualizar o campo marcacao do model MarkPoint.</p>"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback(
        "",
        0,
        message=f"<p>Atualizando campo marcacao do model MarkPoint.</p>",
        state=state,
    )
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        marc = MarkPoint.objects.get(pk=marcacao_id)
        dt_marcacao = datetime(
            marc.day.year,
            marc.day.month,
            marc.day.day,
            marc.mark.hour,
            marc.mark.minute,
            marc.mark.second,
        )
        marc.marcacao = dt_marcacao
        marc.save()

        state = "ready"
        message = f"<p>Processamento da atualização do campo marcacao concluído."
    except Exception as err:
        log.exception(err)
        state = "failed"
        message = msg
        task.info(msg=msg, type_of=3)

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()
