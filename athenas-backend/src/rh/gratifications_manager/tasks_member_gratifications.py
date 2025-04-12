import time
import os
from datetime import datetime

from django.db.models import F

from celery import Celery, group

from contrib.utils import getLogger
from contrib.middleware import set_current_user
from contrib.daterange import NewDateRange

from engine.mq.models import Task
from rh.models import PeriodoGratMembros, GratMembros, Servidor

from rh.gratifications_manager.member_gratifications_utils import *

from rh.gfp.gcpp_utils import criar_gcpp

log = getLogger(__name__)
app = Celery("gratificaions_manager")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def consolidar_grat_membros_periodo_task(
    task, hook, user, periodo_id, servidor_id=None
):
    """
    Esta Task é responsável por consolidar os membros de um período para gestão de gratificações
    """

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    periodo = PeriodoGratMembros.objects.get(pk=periodo_id)

    state = "progress"
    msg = f"<p>Erro ao consolidar os membros para gestão de gratificações para o período: {periodo}.</p>"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback(
        "",
        0,
        message=f"<p>Consolidação dos membros para gestão de gratificações para o periodo: {periodo}.</p>",
        state=state,
    )
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        if servidor_id is None:
            membros_ativos = buscar_membros_ativos()
        else:
            membros_ativos = Servidor.objects.filter(pk=servidor_id)
        try:
            inc_progress = 100.0 / membros_ativos.count()
        except ZeroDivisionError:
            inc_progress = 1

        group_job = []
        for servidor in membros_ativos:
            group_job.append(
                consolidar_grat_membro_task.s(
                    task.uuid, inc_progress, user, servidor.matricula, periodo.pk
                )
            )

        periodo.data_ultimo_calculo = datetime.today()
        periodo.save()

        result = None
        job = group(group_job)

        result = job.apply_async()
        while not result.ready():
            time.sleep(2)

        state = "ready"
        message = f"Consolidação dos membros para gestão de gratificações para o periodo: {periodo} concluída com sucesso."
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
def consolidar_grat_membro_task(task_uuid, inc_progress, user, matricula, periodo_id):
    task = Task.objects.get(uuid=task_uuid) if task_uuid else None

    servidor = Servidor.objects.get(matricula=matricula)

    periodo = PeriodoGratMembros.objects.get(pk=periodo_id)
    range_periodo = NewDateRange.range_from_month(periodo.ano, periodo.mes)
    dt_range_periodo = NewDateRange(range_periodo[0], range_periodo[1])
    try:
        if verificar_posse_servidor(servidor, dt_range_periodo):
            designacoes = buscar_designacoes(servidor, dt_range_periodo)
            grat_membro = criar_grat_membro(servidor, designacoes, periodo, user)

            gratificacoes = buscar_gratificacoes(
                designacoes, dt_range_periodo, servidor.tipo
            )
            gratificacoes_filtradas = filtrar_gratificacoes(
                grat_membro, gratificacoes, designacoes, dt_range_periodo, user
            )
            gravar_gratificacoes(periodo, grat_membro, gratificacoes_filtradas, user)
    except Exception as e:
        if task:
            task.info(
                msg=f"<p>Erro ao consolidar o membro {servidor} para gestão de gratificações.</p>",
                type_of=3,
            )

    if task:
        Task.objects.filter(pk=task.pk).update(progress=F("progress") + inc_progress)


@app.task()
def deferir_todos_gratificacoes_membro_task(task, hook, user, grat_membro_id):
    """
    Esta Task é responsável por deferir as gratificações de um membro.s
    """

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    grat_membro = GratMembros.objects.get(pk=grat_membro_id)

    membro_nome = grat_membro.servidor.pessoa_fisica.social_name
    membro_periodo = grat_membro.periodo

    state = "progress"
    msg = f"<p>Erro ao deferir as gratificações do membro {membro_nome} no periodo {membro_periodo}.</p>"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback(
        "",
        0,
        message=f"<p>Erro ao deferir as gratificações do membro {membro_nome} no periodo {membro_periodo}..</p>",
        state=state,
    )
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        q_gratificacao = Gratificacao.objects.filter(
            grat_membro=grat_membro, status="AVAL"
        )

        msg_log = ""

        for gratificacao in q_gratificacao:
            gratificacao.status = "DEFER"
            if gratificacao.qtd_dias_deferido is None:
                gratificacao.qtd_dias_deferido = gratificacao.qtd_dias_consolidado

            gratificacao.save()

            if gratificacao.qtd_dias_deferido == 0:
                msg_log = (
                    msg_log
                    + f"""<p> {gratificacao} -  Registro de gratificação deferido. Como a quantidade de dias deferido é zero,
                não foi registrado no GCPP.</p>"""
                )
            else:
                criar_gcpp(
                    servidor=gratificacao.grat_membro.servidor,
                    evento=gratificacao.evento,
                    qtd_dias=gratificacao.qtd_dias_deferido,
                    periodo_ano=gratificacao.grat_membro.periodo.ano,
                    periodo_mes=gratificacao.grat_membro.periodo.mes,
                    servidor_conferido_por=Servidor.objects.get(
                        user=get_current_user()
                    ),
                    modulo_origem="gratificações",
                )
                msg_log = (
                    msg_log
                    + f"<p> {gratificacao} -Registro de gratificação deferido e registrado no GCPP com sucesso. </p>"
                )

        state = "ready"
        message = f"Deferir todas as Gratificações do {membro_nome} do periodo {membro_periodo}. concluída com sucesso. {msg_log}"
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
