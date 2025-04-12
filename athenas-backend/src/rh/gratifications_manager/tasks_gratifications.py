import time
import os

from celery import Celery, group
from contrib.utils import getLogger
from contrib.middleware import set_current_user

from engine.mq.models import Task

from rh.gratifications_manager.tasks_gm import marcar_conferencia

log = getLogger(__name__)
app = Celery("gfp")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def conferir_gratificacoes_task(task, hook, user, gratificacoes, conferido_por_id):
    """
    Esta Task é responsável por criar a conferência de Gratificações
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
    msg = f"<p>Erro ao conferir as gratificações.</p>"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback("", 0, message=f"<p>Conferindo gratificações.</p>", state=state)
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        try:
            inc_progress = 100.0 / len(gratificacoes)
        except ZeroDivisionError:
            inc_progress = 1

        group_job = []
        for gratif in gratificacoes:
            periodo_ano = gratif["periodo_ano"]
            periodo_mes = gratif["periodo_mes"]
            evento_numero = gratif["evento_numero"]
            group_job.append(
                marcar_conferencia.s(
                    task.uuid,
                    inc_progress,
                    gratif,
                    periodo_ano,
                    periodo_mes,
                    evento_numero,
                    conferido_por_id,
                    "gratificações",
                )
            )

        result = None
        job = group(group_job)

        result = job.apply_async()
        while not result.ready():
            time.sleep(2)

        state = "ready"
        message = f"<p>Processamento das conferências das gratificações concluído."
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
