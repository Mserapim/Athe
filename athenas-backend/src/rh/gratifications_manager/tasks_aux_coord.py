import time
import os
from datetime import datetime

from django.db.models import Q, F
from celery import Celery, group

from contrib.utils import getLogger
from contrib.middleware import set_current_user
from contrib.daterange import NewDateRange

from engine.mq.models import Task
from rh.models import MovimentacaoAuxiliarCoordenacao, GratAuxiliarCoordenacao
from rh.gfp.models import Evento

from rh.gratifications_manager.gm_utils import buscar_folha
from rh.gfp.paycheckdifference_utils import calc_from_period

from rh.gratifications_manager.gm_utils import buscar_registro_gcpp


log = getLogger(__name__)
app = Celery("gfp")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def calcular_movs_auxs_coords_task(task, hook, user, periodo_ano, periodo_mes):
    """
    Esta Task é responsável por calcular registros de Auxílio Coordenação
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
    msg = f"<p>Erro ao calcular os registros de Auxílio Coordenação do período: {periodo_ano}/{periodo_mes}</p>"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback(
        "",
        0,
        message=f"<p>Cálculo dos registros de Auxílio Coordenação do periodo: {periodo_ano}/{periodo_mes}.</p>",
        state=state,
    )
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        range_periodo = NewDateRange.range_from_month(
            int(periodo_ano), int(periodo_mes)
        )
        q_movs_auxs_coords = MovimentacaoAuxiliarCoordenacao.objects.filter(
            Q(data_inicio__lte=range_periodo[1])
        ).filter(Q(data_fim__gte=range_periodo[0]) | Q(data_fim__isnull=True))

        q_grat_aux_coord = GratAuxiliarCoordenacao.objects.filter(
            mov_aux_coord__in=q_movs_auxs_coords,
            ano=periodo_ano,
            mes=periodo_mes,
            status__in=["DEFER", "INDEFER"],
        )
        excluir_auxs_coords_ids = [
            mov_aux_coord.mov_aux_coord.pk for mov_aux_coord in q_grat_aux_coord
        ]

        movs_auxs_coords = q_movs_auxs_coords.exclude(pk__in=excluir_auxs_coords_ids)

        try:
            inc_progress = 100.0 / movs_auxs_coords.count()
        except ZeroDivisionError:
            inc_progress = 1

        group_job = []
        for mov_aux_coord in movs_auxs_coords:
            group_job.append(
                calcular_mov_aux_coord_task.s(
                    task.uuid,
                    inc_progress,
                    user,
                    mov_aux_coord.pk,
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
        message = f"Cálculo dos registros de Auxílio Coordenação do periodo: {periodo_ano}/{periodo_mes} concluída com sucesso."
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
def calcular_mov_aux_coord_task(
    task_uuid, inc_progress, user, aux_coord_id, periodo_ano, periodo_mes
):
    """
    Esta Task é responsável por calcular um registro de Auxílio Coordenação
    """

    task = Task.objects.get(uuid=task_uuid) if task_uuid else None
    set_current_user(user)

    try:
        mov_aux_coord = MovimentacaoAuxiliarCoordenacao.objects.get(pk=aux_coord_id)
        if "CAAD" in mov_aux_coord.servidor_designacao.lotacao.nome:
            evento = Evento.objects.get(numero="12400")  # grat. função coord. 30% CAAD
        else:
            evento = Evento.objects.get(numero="11400")  # grat. função coord. 10%

        grat_aux_coord = GratAuxiliarCoordenacao.objects.filter(
            mov_aux_coord=mov_aux_coord,
            ano=periodo_ano,
            mes=periodo_mes,
            evento=evento,
        )
        if grat_aux_coord.exists():
            grat_aux_coord = grat_aux_coord.first()
        else:
            grat_aux_coord = GratAuxiliarCoordenacao(
                mov_aux_coord=mov_aux_coord,
                ano=periodo_ano,
                mes=periodo_mes,
                evento=evento,
            )

        folha = buscar_folha(periodo_ano, periodo_mes)

        res_titular = calc_from_period(
            grat_aux_coord.mov_aux_coord.servidor, folha.first(), evento
        )
        grat_aux_coord.qtd_dias_consolidado_titular = int(res_titular["qnt"])

        range_periodo = NewDateRange.range_from_month(
            int(grat_aux_coord.ano), int(grat_aux_coord.mes)
        )
        dt_range_periodo = NewDateRange(range_periodo[0], range_periodo[1])
        if grat_aux_coord.mov_aux_coord.substituto:
            res_substituto = calc_from_period(
                grat_aux_coord.mov_aux_coord.substituto, folha.first(), evento
            )
            grat_aux_coord.qtd_dias_consolidado_substituto = int(res_substituto["qnt"])

        grat_aux_coord.status = "AVAL"
        grat_aux_coord.data_ultimo_calculo = datetime.today()
        grat_aux_coord.save()
    except Exception as e:
        if task:
            task.info(
                msg=f"<p>Erro ao calcular o registro de Auxílio Coordenação: {mov_aux_coord}.</p>",
                type_of=3,
            )

    if task:
        Task.objects.filter(pk=task.pk).update(progress=F("progress") + inc_progress)


@app.task()
def deferir_movs_auxs_coords_task(task, hook, user, periodo_ano, periodo_mes):
    """
    Esta Task é responsável por deferir registros de Auxílio Coordenação
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
    msg = f"<p>Erro ao deferir os registros de Auxílio Coordenação do período: {periodo_ano}/{periodo_mes}</p>"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback(
        "",
        0,
        message=f"<p>Deferimento dos registros de Auxílio Coordenação do periodo: {periodo_ano}/{periodo_mes}.</p>",
        state=state,
    )
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        range_periodo = NewDateRange.range_from_month(
            int(periodo_ano), int(periodo_mes)
        )
        q_movs_auxs_coords = MovimentacaoAuxiliarCoordenacao.objects.filter(
            Q(data_inicio__lte=range_periodo[1])
        ).filter(Q(data_fim__gte=range_periodo[0]) | Q(data_fim__isnull=True))

        q_grat_aux_coord = GratAuxiliarCoordenacao.objects.filter(
            mov_aux_coord__in=q_movs_auxs_coords,
            ano=periodo_ano,
            mes=periodo_mes,
            status__in=["DEFER", "INDEFER"],
            evento=Evento.objects.get(numero="11400"),
        )
        excluir_auxs_coords_ids = [
            mov_aux_coord.mov_aux_coord.pk for mov_aux_coord in q_grat_aux_coord
        ]

        movs_auxs_coords = q_movs_auxs_coords.exclude(pk__in=excluir_auxs_coords_ids)

        try:
            inc_progress = 100.0 / movs_auxs_coords.count()
        except ZeroDivisionError:
            inc_progress = 1

        group_job = []
        for mov_aux_coord in movs_auxs_coords:
            group_job.append(
                deferir_mov_aux_coord_task.s(
                    task.uuid,
                    inc_progress,
                    user,
                    mov_aux_coord.pk,
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
        message = f"Deferimento dos registros de Auxílio Coordenação do periodo: {periodo_ano}/{periodo_mes} concluída com sucesso."
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
def deferir_mov_aux_coord_task(
    task_uuid, inc_progress, user, aux_coord_id, periodo_ano, periodo_mes
):
    """
    Esta Task é responsável por deferir um registro de Auxílio Coordenação
    """

    task = Task.objects.get(uuid=task_uuid) if task_uuid else None
    set_current_user(user)

    try:
        mov_aux_coord = MovimentacaoAuxiliarCoordenacao.objects.get(pk=aux_coord_id)
        evento = Evento.objects.get(numero="11400")

        obj = {
            "success": True,
            "message": "",
        }

        grat_aux_coord = GratAuxiliarCoordenacao.objects.get(
            mov_aux_coord=mov_aux_coord,
            ano=periodo_ano,
            mes=periodo_mes,
            evento=evento,
        )

        gcpp_titular = buscar_registro_gcpp(
            grat_aux_coord.mov_aux_coord.servidor,
            grat_aux_coord.evento,
            grat_aux_coord.ano,
            grat_aux_coord.mes,
        )

        if mov_aux_coord.substituto:
            gcpp_substituto = buscar_registro_gcpp(
                grat_aux_coord.mov_aux_coord.substituto,
                grat_aux_coord.evento,
                grat_aux_coord.ano,
                grat_aux_coord.mes,
            )

        if (gcpp_titular.exists() and gcpp_titular.first().status == "pago") or (
            mov_aux_coord.substituto
            and gcpp_substituto.exists()
            and gcpp_substituto.first().status == "pago"
        ):
            obj["success"] = False
            obj["message"] = (
                "O registro de gratificação selecionado já está deferido e pago no GCPP para o titular e/ou substituto."
            )
        elif (gcpp_titular.exists() and gcpp_titular.first().status == "inapto") or (
            mov_aux_coord.substituto
            and gcpp_substituto.exists()
            and gcpp_substituto.first().status == "inapto"
        ):
            obj["message"] = (
                f"O registro de gratificação selecionado já está deferido e está inapto para pagamento no GCPP para o titular e/ou substituto."
            )
        else:
            grat_aux_coord.status = "DEFER"
            if grat_aux_coord.qtd_dias_deferido_titular is None:
                grat_aux_coord.qtd_dias_deferido_titular = (
                    grat_aux_coord.qtd_dias_consolidado_titular
                )

            if (
                mov_aux_coord.substituto
                and grat_aux_coord.qtd_dias_deferido_substituto is None
            ):
                grat_aux_coord.qtd_dias_deferido_substituto = (
                    grat_aux_coord.qtd_dias_consolidado_substituto
                )

            grat_aux_coord.save()

            if grat_aux_coord.qtd_dias_deferido_titular in [0, None]:
                obj["message"] = (
                    f"Registro de gratificação do titular deferido. Como a quantidade de dias deferido é zero, não foi registrado no GCPP."
                )
            else:
                # registro gcpp está sendo criado no método save de GratAuxiliarCoordenacao
                obj["message"] = f"Registro do titular deferido e registrado no GCPP."

            if mov_aux_coord.substituto:
                if grat_aux_coord.qtd_dias_deferido_substituto in [0, None]:
                    obj[
                        "message"
                    ] += f"Registro do substituto deferido. Como a quantidade de dias deferido é zero, não foi registrado no GCPP."
                else:
                    # registro gcpp está sendo criado no método save de GratAuxiliarCoordenacao
                    obj[
                        "message"
                    ] += f"Registro do substituto deferido e registrado no GCPP."

        if task:
            if obj["success"]:
                task.info(msg=f"<p>{obj['message']}.</p>")
            else:
                task.info(msg=f"<p>{obj['message']}.</p>", type_of=3)

    except Exception as e:
        if task:
            task.info(
                msg=f"<p>Erro ao deferir o registro de Auxílio Coordenação: {mov_aux_coord}.</p>",
                type_of=3,
            )

    if task:
        Task.objects.filter(pk=task.pk).update(progress=F("progress") + inc_progress)
