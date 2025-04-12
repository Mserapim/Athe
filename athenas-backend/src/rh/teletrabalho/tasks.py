import os

from celery import Celery
from datetime import datetime

from contrib.middleware import set_current_user

from engine.mq.models import Task
from rh.const import STATUS_TELETRABALHO_REGULAR
from rh.models import MovimentacaoTeletrabalho
from common.services.models import ScheduledServices

from logging import getLogger
from celery import Celery, group
from django.db.models import F, Sum
import time

from rh.teletrabalho.utils import bloquear_mov_teletrabalho, mov_teletrabalhos_pendentes
from rh.teletrabalho.notificacoes import enviar_notificacao_email_gestor


log = getLogger(__name__)

app = Celery("teletrabalho")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task()
def atualiza_status_teletrabalho_task(task, hook, tele_pk, ativo, user):
    """
    Está Task é responsável por atualizar o status do teletrabalho

    Args:
    :tele_pk: (str) ID da MovimentacaoTeletrabalho.
    :ativo: (bool) Status do teletrabalho.
    :user: (str) ID do usuário logado.

    """

    state = "failed"
    task = Task.objects.get(uuid=task)

    has_exception = None

    try:
        set_current_user(user)

        task.message = "<p>Alterando status...</p>"
        task.state = "progress"
        task.save()

        query = MovimentacaoTeletrabalho.objects.filter(pk=tele_pk)
        query.update(ativo=ativo)
        log.info(f"Status do teletrabalho atualizado: {query.first()}")

        message = f"Status do teletrabalho atualizado com sucesso: {query.first()}"
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar atualizar o status do teletrabalho!" % (err)

    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def bloquear_mov_teletrabalhos_pendentes_task(
    task, mov_tele_pk=None, user=None, inc_progress=None
):
    """
    Está Task é responsável por verificar a bloquar Movimentacao teletrabalho

    Args:
    :tele_pk: (str) ID da MovimentacaoTeletrabalho.
    :data_atual: (date) Data atual.
    :user: (str) ID do usuário logado.

    """

    state = "failed"
    task = Task.objects.get(uuid=task)

    has_exception = None

    try:
        set_current_user(user)

        task.message = "<p>Verificação de bloqueio...</p>"
        task.state = "progress"
        task.save()
        mov_tele = MovimentacaoTeletrabalho.objects.get(pk=mov_tele_pk)
        bloquear_mov_teletrabalho(mov_tele)

        message = f"teletrabalho: {mov_tele} - {mov_tele.pk}"
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar bloquear o teletrabalho!" % (err)

    task.message = message
    task.add_message(message)
    task.finish_execution(status=state)
    task.state = state
    Task.objects.filter(uuid=task).update(progress=F("progress") + inc_progress)
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def bloquear_tele_pendentes_task(task, hook, user=None):
    task = Task.objects.get(uuid=task)
    task.message = "<p>Verificação de bloqueio do teletrabalho...</p>"
    task.state = "progress"
    task.save()
    task.add_message(task.message)

    data_atual = datetime.today().date()
    inicio_mes = datetime(data_atual.year, data_atual.month, 1)
    movs_teletrabalhos = MovimentacaoTeletrabalho.objects.filter(
        servidor__ativo=True,
        situacao__in=[STATUS_TELETRABALHO_REGULAR],
        data_inicio__lt=inicio_mes,
    )

    total = movs_teletrabalhos.count()
    inc_progress = 100.0 / total if total else 0
    result = None

    movs_teletrabalhos_a_bloquear = mov_teletrabalhos_pendentes(
        movs_teletrabalhos, data_atual
    )

    jobs = []
    for mov_tele in movs_teletrabalhos_a_bloquear:
        jobs.append(
            bloquear_mov_teletrabalhos_pendentes_task.s(
                task.uuid,
                mov_tele_pk=mov_tele.pk,
                user=user,
                inc_progress=inc_progress,
            )
        )

    job = group(jobs)
    result = job.apply_async()

    while not result.ready():
        time.sleep(2)

    enviar_notificacao_email_gestor(movs_teletrabalhos_a_bloquear)

    task.info(pct_progress=100)
    task.finish_execution()
