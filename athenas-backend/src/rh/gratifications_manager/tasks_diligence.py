import time
import os
from datetime import datetime

from django.db.models import Q, F
from celery import Celery, group

from contrib.utils import getLogger
from contrib.middleware import set_current_user
from contrib.daterange import NewDateRange

from engine.mq.models import Task
from rh.models import MovimentacaoDiligencia, GratDiligencia
from rh.gfp.models import Evento

from rh.gratifications_manager.gm_utils import buscar_folha
from rh.gfp.paycheckdifference_utils import calc_from_period

log = getLogger(__name__)
app = Celery("gfp")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def calcular_movs_diligs_task(task, hook, user, periodo_ano, periodo_mes):
    """
    Esta Task é responsável por calcular registros de Designação para Diligência
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
    msg = f"<p>Erro ao calcular os registros de Designação para Diligência do período: {periodo_ano}/{periodo_mes}</p>"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback(
        "",
        0,
        message=f"<p>Cálculo dos registros de Designação para Diligência do periodo: {periodo_ano}/{periodo_mes}.</p>",
        state=state,
    )
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        range_periodo = NewDateRange.range_from_month(
            int(periodo_ano), int(periodo_mes)
        )
        q_movs_diligs = MovimentacaoDiligencia.objects.filter(
            Q(data_inicio__lte=range_periodo[1])
        ).filter(Q(data_fim__gte=range_periodo[0]) | Q(data_fim__isnull=True))

        q_grat_diligencia = GratDiligencia.objects.filter(
            mov_diligencia__in=q_movs_diligs,
            ano=periodo_ano,
            mes=periodo_mes,
            status__in=["DEFER", "INDEFER"],
        )
        excluir_diligs_ids = [
            mov_diligencia.mov_diligencia.pk for mov_diligencia in q_grat_diligencia
        ]

        movs_diligs = q_movs_diligs.exclude(pk__in=excluir_diligs_ids)

        try:
            inc_progress = 100.0 / movs_diligs.count()
        except ZeroDivisionError:
            inc_progress = 1

        group_job = []
        for mov_diligencia in movs_diligs:
            group_job.append(
                calcular_mov_diligencia_task.s(
                    task.uuid,
                    inc_progress,
                    user,
                    mov_diligencia.pk,
                    periodo_ano,
                    periodo_mes,
                )
            )

        result = None
        job = group(group_job)

        result = job.apply_async()
        while not result.ready():
            time.sleep(2)

        state = "ready"
        message = f"Cálculo dos registros de Designação para Diligência do periodo: {periodo_ano}/{periodo_mes} concluída com sucesso."
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


@app.task()
def calcular_mov_diligencia_task(
    task_uuid, inc_progress, user, aux_coord_id, periodo_ano, periodo_mes
):
    """
    Esta Task é responsável por calcular um registro de Designação para Diligência
    """

    task = Task.objects.get(uuid=task_uuid) if task_uuid else None
    set_current_user(user)

    try:
        mov_diligencia = MovimentacaoDiligencia.objects.get(pk=aux_coord_id)
        evento = Evento.objects.get(numero="12000")

        grat_diligencia = GratDiligencia.objects.filter(
            mov_diligencia=mov_diligencia,
            ano=periodo_ano,
            mes=periodo_mes,
            evento=evento,
        )
        if grat_diligencia.exists():
            grat_diligencia = grat_diligencia.first()
        else:
            grat_diligencia = GratDiligencia(
                mov_diligencia=mov_diligencia,
                ano=periodo_ano,
                mes=periodo_mes,
                evento=evento,
            )

        folha = buscar_folha(periodo_ano, periodo_mes)

        res_titular = calc_from_period(
            grat_diligencia.mov_diligencia.servidor, folha.first(), evento
        )
        grat_diligencia.qtd_dias_consolidado_titular = int(res_titular["qnt"])

        range_periodo = NewDateRange.range_from_month(
            int(grat_diligencia.ano), int(grat_diligencia.mes)
        )
        dt_range_periodo = NewDateRange(range_periodo[0], range_periodo[1])
        if grat_diligencia.mov_diligencia.substituto and (
            grat_diligencia.qtd_dias_consolidado_titular != dt_range_periodo.days
        ):
            res_substituto = calc_from_period(
                grat_diligencia.mov_diligencia.substituto, folha.first(), evento
            )
            grat_diligencia.qtd_dias_consolidado_substituto = int(res_substituto["qnt"])

        grat_diligencia.status = "AVAL"
        grat_diligencia.data_ultimo_calculo = datetime.today()
        grat_diligencia.save()
    except Exception as e:
        if task:
            task.info(
                msg=f"<p>Erro ao calcular o registro de Designação para Diligência: {mov_diligencia}.</p>",
                type_of=3,
            )

    if task:
        Task.objects.filter(pk=task.pk).update(progress=F("progress") + inc_progress)
