import time
import os
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Max

from celery import Celery

from contrib.utils import getLogger
from contrib.middleware import set_current_user
from contrib.daterange import NewDateRange

from engine.mq.models import Task
from rh.models import (
    PeriodoExercCumulPermanente,
    ExercCumulPermanente,
    DesigsExercCumulPermanente,
    Servidor,
)

from rh.gratifications_manager.cumulative_exercises_permanent_utils import *
from rh.afastamento.afastamento_utils import buscar_afastamentos_periodo

log = getLogger(__name__)
app = Celery("gratificaions_manager")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def consolidar_periodo_task(task, hook, user, periodo_id):
    """
    Esta Task é responsável por consolidar exercícios cumulativos permanentes de um período
    """

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    task = Task.objects.get(uuid=task)
    periodo = PeriodoExercCumulPermanente.objects.get(pk=periodo_id)
    range_periodo = NewDateRange.range_from_month(periodo.ano, periodo.mes)
    dt_range_periodo = NewDateRange(range_periodo[0], range_periodo[1])

    try:
        set_current_user(User.objects.get(username="athenas"))

        desigs = buscar_desigs(dt_range_periodo)
        matriculas = buscar_matriculas_desigs(desigs)

        exercs_cumul_perm_ignorar = ExercCumulPermanente.objects.filter(
            periodo=periodo, status__in=["DEFER", "INDEFER"]
        )
        matriculas_ignorar = [x.servidor.matricula for x in exercs_cumul_perm_ignorar]

        ExercCumulPermanente.objects.filter(periodo=periodo, status="AVAL").delete()

        for matricula in matriculas:
            calcular_exerc_cumul_permanente(
                periodo, matriculas_ignorar, matricula, desigs, dt_range_periodo
            )

        periodo.data_ultimo_calculo = datetime.now()
        periodo.save()

        state = "progress"
        msg = f"Consolidação dos exercícios cumulativos para o periodo: {periodo} concluída com sucesso."

        log.debug(msg)
        feedback("", 0, message=f"<p>{msg}</p>", state=state)
        task.info(
            msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )

        set_current_user(user)
    except Exception as err:
        log.exception(err)
        state = "failed"
        msg = f"<p>Erro ao consolidar exercícios cumulativos para o período: {periodo}.</p>"
        task.info(msg=msg, type_of=3)

    feedback("", 100)
    task.message = msg
    task.finish_execution(status=state)
    task.state = state
    task.save()
