import time
import os

from contrib.utils import getLogger
from contrib.middleware import set_current_user

from django.db.models import F
from celery import Celery, group
from engine.mq.models import Task

from standard.models import Choice
from nomeacao.models import DocumentoConvidado

from nomeacao.cadastramento.sinc_form_nomeacao_residente import (
    SincFormNomeacaoResidentes,
)

log = getLogger(__name__)
app = Celery("gfp")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def sinc_form_cpf_nomeacao_residente_task(task, hook, user):
    """
    Esta Task é responsável por sincronizar dados de todos os CPFs que foram convidados à nomeacao de residente
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
    msg = f"<p>Erro ao sincronizar os CPFs para nomeação de residente.</p>"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback(
        "",
        0,
        message=f"<p>Sincronização dos CPFs para nomeação de residente.</p>",
        state=state,
    )
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        tipo_nomeacao = (
            Choice.objects.filter(
                app_label="nomeacao", name="TIPO_NOMEACAO", label="Residente"
            )
            .first()
            .value
        )
        q_docs = DocumentoConvidado.objects.filter(
            convidado__convite_nomeacao__tipo_nomeacao=tipo_nomeacao
        )
        cpfs_nao_buscar = [doc.cpf for doc in q_docs]

        q_lista_cpfs = SincFormNomeacaoResidentes().buscar_lista_cpfs(cpfs_nao_buscar)

        try:
            inc_progress = 100.0 / len(q_lista_cpfs)
        except ZeroDivisionError:
            inc_progress = 1

        group_job = []
        for cpf in q_lista_cpfs:
            group_job.append(
                sinc_cpf_nomeacao_residente_subtask.s(
                    task.uuid, inc_progress, user, cpf
                )
            )

        result = None
        job = group(group_job)

        result = job.apply_async()
        while not result.ready():
            time.sleep(2)

        state = "ready"
        message = (
            f"Sincronização dos CPFs para nomeação de residentes concluída com sucesso."
        )
    except Exception as err:
        log.error(err)
        state = "failed"
        message = msg
        task.info(msg=msg, type_of=3)

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def sinc_cpf_nomeacao_residente_subtask(task_uuid, inc_progress, user, cpf):
    """
    Esta Task é responsável por sincronizar dados de um CPF que foi convidado à nomeacao de residente
    """

    task = Task.objects.get(uuid=task_uuid) if task_uuid else None
    set_current_user(user)

    try:
        SincFormNomeacaoResidentes().sinc_cpf(cpf)
    except Exception as e:
        if task:
            task.info(
                msg=f"<p>Erro ao sincronizar dados de nomeação à residentes do CPF: {cpf}.</p>",
                type_of=3,
            )

    if task:
        Task.objects.filter(pk=task.pk).update(progress=F("progress") + inc_progress)


@app.task()
def sinc_cpf_nomeacao_residente_task(task, hook, user, cpf):
    """
    Esta Task é responsável por sincronizar dados de um CPF convidado à nomeacao de residente
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
    msg = f"<p>Erro ao sincronizar nomeação de residente para o CPF: {cpf}.</p>"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback(
        "",
        0,
        message=f"<p>Sincronização para nomeação de residente para o CPF: {cpf}.</p>",
        state=state,
    )
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        SincFormNomeacaoResidentes().sinc_cpf(cpf)

        state = "ready"
        message = f"Sincronização para nomeação de residente para o CPF {cpf} concluída com sucesso."
    except Exception as err:
        log.error(err)
        state = "failed"
        message = msg
        task.info(msg=msg, type_of=3)

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()
