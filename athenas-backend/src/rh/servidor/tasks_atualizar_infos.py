import time
import os

from contrib.utils import getLogger
from contrib.middleware import set_current_user

from celery import Celery
from engine.mq.models import Task

from rh.gfp.models import Servidor

from rh.servidor.mastiff_utils import MastiffGraphql
from rh.servidor.atualizar_infos_utils import (
    verificar_infos_para_atualizar,
    atualizar_infos,
)


log = getLogger(__name__)
app = Celery("rh")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def atualizar_username_task(task, hook, user, servidor_id, cpf_mascarado):
    """
    Esta Task é responsável por atualizar o username do Servidor em relação ao AD
    """

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    servidor = Servidor.objects.get(pk=servidor_id)

    state = "progress"
    msg = f"Atualização de username do Servidor: {servidor}"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback("", 0, message=f"<p>{msg} iniciada.</p>", state=state)
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        infos_mastiff = MastiffGraphql().buscar_infos_usuario_mastiff(cpf_mascarado)

        infos_atualizar = verificar_infos_para_atualizar(
            servidor, infos_mastiff["username"]
        )
        atualizar_infos(servidor, infos_mastiff, infos_atualizar)

        state = "ready"
        message = f"{msg} concluída com sucesso."
    except Exception as err:
        msg = f"Erro na atualização de username do Servidor: {servidor}"
        log.info(f">>> {msg}")
        log.error(err)
        state = "failed"
        message = msg
        task.info(msg=msg, type_of=3)

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()
