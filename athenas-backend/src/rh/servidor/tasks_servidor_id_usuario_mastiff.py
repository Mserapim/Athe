import time
import os
from contrib.utils import getLogger
from contrib.middleware import set_current_user
from celery import Celery
from engine.mq.models import Task
from rh.models import Servidor
from rh.servidor.mastiff_utils import MastiffGraphql


log = getLogger(__name__)
app = Celery("rh")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def atualizar_id_usuario_mastiff_task(task, hook, user, servidor_id, cpf_mascarado):
    """
    Esta Task é responsável por atualizar o id_usuario_mastiff do Servidor
    """

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    servidor = Servidor.objects.filter(pk=servidor_id)

    state = "progress"
    msg = f"Atualização de id_usuario_mastiff do Servidor: {servidor}"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback("", 0, message=f"<p>{msg} iniciada.</p>", state=state)
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        infos_mastiff = MastiffGraphql().buscar_infos_usuario_mastiff(cpf_mascarado)
        servidor.update(id_usuario_mastiff=infos_mastiff["id_usuario_mastiff"])
        state = "ready"
        message = f"{msg} concluída com sucesso."
    except Exception as err:
        msg = f"Erro na atualização de id_usuario_mastiff do Servidor: {servidor}. Erro: {err}"
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
