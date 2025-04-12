import time
import os

from django.db.models import Q

from celery import Celery

from contrib.utils import getLogger
from contrib.middleware import set_current_user

from engine.mq.models import Task
from rh.models import ControlePagamentoPessoal

from rh.gfp.gcpp_utils import (
    calcular_e_salvar_gcpp,
    confirmar_e_salvar_gcpp,
    declinar_e_salvar_gcpp,
    aplicar_e_salvar_gcpp,
)

log = getLogger(__name__)
app = Celery("gratificaions_manager")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def calcular_gcpps_task(task, hook, user, gcpp_ids):
    """
    Esta Task é responsável por calcular registro(s) de Gestão de Controle de Pagamento de Pessoal.
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
    gcpps = ControlePagamentoPessoal.objects.filter(pk__in=gcpp_ids)

    state = "progress"
    msg = f"Calculando Pagamento de Pessoal."

    log.debug(msg)
    feedback("", 0, message=f"<p>{msg}</p>", state=state)
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    set_current_user(user)
    titulo_folha = "NORMAL"

    try:
        for gcpp in gcpps:
            titulo_folha = (
                "ESTAGIÁRIOS"
                if gcpp.servidor.type_by_possession == "EST"
                else (
                    "RESIDENTES"
                    if gcpp.servidor.type_by_possession == "EST"
                    else "NORMAL"
                )
            )
            calcular_e_salvar_gcpp(gcpp, titulo_folha=titulo_folha)
    except Exception as err:
        log.exception(err)
        state = "failed"
        msg = f"<p>ERRO ao calcular Pagamento de Pessoal.</p>"
        task.info(msg=msg, type_of=3)

    feedback("", 100)
    task.message = msg
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def confirmar_gcpps_task(task, hook, user, gcpp_ids):
    """
    Esta Task é responsável por confirmar registro(s) de Gestão de Controle de Pagamento de Pessoal.
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
    gcpps = ControlePagamentoPessoal.objects.filter(pk__in=gcpp_ids)

    state = "progress"
    msg = f"Confirmando Pagamento de Pessoal."

    log.debug(msg)
    feedback("", 0, message=f"<p>{msg}</p>", state=state)
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    set_current_user(user)

    try:
        for gcpp in gcpps:
            confirmar_e_salvar_gcpp(gcpp)
    except Exception as err:
        log.exception(err)
        state = "failed"
        msg = f"<p>ERRO ao confirmar Pagamento de Pessoal.</p>"
        task.info(msg=msg, type_of=3)

    feedback("", 100)
    task.message = msg
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def declinar_gcpps_task(task, hook, user, gcpp_ids):
    """
    Esta Task é responsável por declinar registro(s) de Gestão de Controle de Pagamento de Pessoal.
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
    gcpps = ControlePagamentoPessoal.objects.filter(pk__in=gcpp_ids)

    state = "progress"
    msg = f"Declinando Pagamento de Pessoal."

    log.debug(msg)
    feedback("", 0, message=f"<p>{msg}</p>", state=state)
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    set_current_user(user)

    try:
        for gcpp in gcpps:
            declinar_e_salvar_gcpp(gcpp)
    except Exception as err:
        log.exception(err)
        state = "failed"
        msg = f"<p>ERRO ao declinar Pagamento de Pessoal.</p>"
        task.info(msg=msg, type_of=3)

    feedback("", 100)
    task.message = msg
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def aplicar_pgto_task(task, hook, user, gcpp_id, folha_id):
    """
    Esta Task é responsável por aplicar em folha registro(s) de Gestão de Controle de Pagamento de Pessoal.
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

    state = "progress"
    msg = f"Aplicando em folha registro(s) de Pagamento de Pessoal."

    log.debug(msg)
    feedback("", 0, message=f"<p>{msg}</p>", state=state)
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    set_current_user(user)

    try:
        res_aplicar_gcpp = aplicar_e_salvar_gcpp(gcpp_id, folha_id)
        if res_aplicar_gcpp["success"] is False:
            state = "failed"
            msg = f"<p>{res_aplicar_gcpp['message']}</p>"
    except Exception as err:
        log.exception(err)
        state = "failed"
        msg = (
            f"<p>ERRO ao aplicar em folha o(s) registro(s) de Pagamento de Pessoal.</p>"
        )
        task.info(msg=msg, type_of=3)

    feedback("", 100)
    task.message = msg
    task.finish_execution(status=state)
    task.state = state
    task.save()
