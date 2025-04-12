import os

from celery import Celery
from contrib.utils import getLogger

from django.db.models import F

from engine.mq.models import Task
from rh.gfp.models import Servidor, Evento

from rh.gratifications_manager.gm_utils import buscar_registro_gcpp
from rh.gfp.gcpp_utils import criar_gcpp

log = getLogger(__name__)
app = Celery("gfp")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def marcar_conferencia(
    task_uuid,
    inc_progress,
    registro,
    periodo_ano,
    periodo_mes,
    evento_numero,
    conferido_por_id,
    modulo_origem,
):
    task = Task.objects.get(uuid=task_uuid) if task_uuid else None

    servidor = Servidor.objects.get(pk=registro["servidor_id"])
    try:
        evento = Evento.objects.get(numero=evento_numero)
        conferencia_servidor = buscar_registro_gcpp(
            servidor, evento, periodo_ano, periodo_mes
        )
        if not conferencia_servidor.exists():
            criar_gcpp(
                servidor=servidor,
                evento=evento,
                qtd_dias=registro["qtd_dias"],
                periodo_ano=periodo_ano,
                periodo_mes=periodo_mes,
                servidor_conferido_por=Servidor.objects.get(pk=conferido_por_id),
                modulo_origem=modulo_origem,
            )
    except Exception as e:
        if task:
            task.info(
                msg=f"Erro {e} ao marcar conferência do servidor {servidor} com a qtd {registro['qtd_dias']}",
                type_of=3,
            )

    if task:
        Task.objects.filter(pk=task.pk).update(progress=F("progress") + inc_progress)
