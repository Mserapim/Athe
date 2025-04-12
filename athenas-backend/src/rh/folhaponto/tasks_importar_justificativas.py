import time
import os

from celery import Celery, group
from contrib.utils import getLogger
from contrib.middleware import set_current_user

from engine.mq.models import Task
from django.db.models import F

from rh.folhaponto.folhaponto_import_justificativas import (
    FolhaPontoImportJustificativa,
    MpFpjustificativa,
)
from standard.models import Item

log = getLogger(__name__)
app = Celery("gfp")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def importar_justificativas_task(task, user, just_ids, inc_progress=0):
    """
    Esta Task é responsável por importar Justificativa do Folha Ponto
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
    msg = f"<p>Erro ao importar Justificativa do Folha Ponto.</p>"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback(
        "", 0, message=f"<p>Importando Justificativa do Folha Ponto.</p>", state=state
    )
    # task.info(msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1)

    try:
        for just_id in just_ids:
            FolhaPontoImportJustificativa().importar_registro_justif_folhaponto(just_id)

        state = "ready"
        message = (
            f"<p>Processamento de importação da Justificativa de Folha Ponto concluído."
        )
    except Exception as err:
        log.exception(err)
        state = "failed"
        message = msg
        task.info(msg=msg, type_of=3)

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    Task.objects.filter(uuid=task).update(progress=F("progress") + inc_progress)
    task.state = state
    task.save()


@app.task()
def importar_justificativas_batch_task(task, hook, user):
    task = Task.objects.get(uuid=task)
    task.message = "<p>Importando justificativa do Folha Ponto...</p>"
    task.state = "progress"
    task.save()

    range_datas = Item.objects.get(key="intervalo_data_importacao").value
    dt_inicio, dt_fim = range_datas.split(",")

    query_justificativas = MpFpjustificativa.objects.only("pk").filter(
        data__isnull=False,
        matricula__isnull=False,
        data__gte=dt_inicio,
        data__lte=dt_fim,
    )

    total = query_justificativas.count()
    inc_progress = 100.0 / total if total else 0

    jobs = []

    batch_size = 10
    justificativa_ids = []
    for justificativa in query_justificativas.iterator():
        justificativa_ids.append(justificativa.pk)
        if len(justificativa_ids) == batch_size:
            jobs.append(
                importar_justificativas_task.s(
                    task.uuid, user, justificativa_ids, inc_progress=inc_progress
                )
            )
            justificativa_ids = []

    if justificativa_ids:
        jobs.append(
            importar_justificativas_task.s(
                task.uuid, user, justificativa_ids, inc_progress=inc_progress
            )
        )

    job = group(jobs)

    job.apply_async()

    task.info(pct_progress=0)
    task.finish_execution(set_process=False)
