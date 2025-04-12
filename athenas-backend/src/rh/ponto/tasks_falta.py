import time
import os

from datetime import datetime, timedelta

from celery import Celery, group
from contrib.middleware import set_current_user, get_current_user

from django.db.models import F, Q
from engine.mq.models import Task
from rh.ponto.models import Falta
from rh.pvf.models import SendingTimeSheet, PointJustification, JustificationItem
from rh.models import MovimentacaoTeletrabalho, Servidor

from rh.ponto.utils import get_start_end_date, registrar_faltas_no_gcpp, query_faltas
from rh.ponto.envio_notificacao_falta import enviar_notificacao_falta
from rh.pvf.const import STS_EFFECTIVE

from contrib.utils import getLogger


log = getLogger(__name__)
app = Celery("ponto")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def processar_faltas_task(
    task, hook, user, employee_id=None, reference=None, falta_ids=None
):
    """
    Esta Task é responsável por processar as faltas do Gestor de Faltas
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
    task = Task.objects.get(uuid=task)
    set_current_user(user)
    competencia = f"- Competência {reference}" if reference else ""
    feedback(
        "", 0, message=f"<p>Processamento de Faltas {competencia}</p>", state=state
    )
    task.info(
        msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        group_job = []
        por_falta = False

        if employee_id:
            # Processa as Faltas de determinados Servidores
            start_date, end_date = get_start_end_date(reference)
            query = query_faltas(employee_id, start_date, end_date, 1)
        elif falta_ids:
            # Processa as Faltas selecionadas
            por_falta = True
            query = Falta.objects.filter(pk__in=falta_ids)

        try:
            inc_progress = 100.0 / query.count()
        except ZeroDivisionError:
            inc_progress = 1

        for falta in query:
            if por_falta:
                reference = f"{falta.data.month}/{falta.data.year}"
            group_job.append(
                precessar_faltas.s(task.uuid, inc_progress, falta.id, reference, user)
            )
            if falta.payroll:
                enviar_notificacao_falta(falta)

        query_gcpp = query.exclude(payroll=False)
        if por_falta:
            # Se a seleção é por Falta, terá apenas um Servidor selecionado
            employee_id = [query.first().servidor.id]
        registrar_faltas_no_gcpp(query_gcpp, employee_id, user)

        result = None
        job = group(group_job)

        result = job.apply_async()
        while not result.ready():
            time.sleep(2)

        state = "ready"
        message = f"<p>Concluído - Quantidade de Faltas processadas: {query.count()} - Competência {reference}."
    except Exception as err:
        log.error(err)
        state = "failed"
        message = f"<p>Erro ao Processar Faltas - Competência {reference}</p>"
        task.info(
            msg=f"<p>Erro ao Processar Faltas - Competência {reference}</p>", type_of=3
        )

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def precessar_faltas(task_uuid, inc_progress, falta_id, reference, user_id):
    task = Task.objects.get(uuid=task_uuid) if task_uuid else None
    set_current_user(user_id)

    falta = Falta.objects.get(id=falta_id)
    try:
        if falta.data_fim:
            falta.situacao = 2
            falta.created_by_id = user_id
            falta.modified_by_id = user_id
            falta.data_processado = datetime.now().date()
            falta.anotacao_falta()
            falta.save()
    except Exception as e:
        if task:
            task.info(
                msg=f"Erro {e} ao processar {falta}, da competência {reference}",
                type_of=3,
            )

    if task:
        Task.objects.filter(pk=task.pk).update(progress=F("progress") + inc_progress)


@app.task()
def atribuir_comp_desc_task(
    task, hook, user, employee_id, reference, competencia_desconto
):
    """
    Esta Task é responsável por atribuir Competência de Desconto às do Gestor de Faltas
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
    task = Task.objects.get(uuid=task)
    set_current_user(user)
    feedback("", 0, message=f"<p>Atribuindo Competência de Desconto</p>", state=state)
    task.info(
        msg=f"Iniciando atribuição - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        group_job = []
        start_date, end_date = get_start_end_date(reference)

        if employee_id:
            query = Falta.objects.filter(
                Q(servidor__id__in=employee_id)
                & Q(situacao=1)
                & Q(
                    Q(
                        Q(data__isnull=False, data_fim__isnull=False)
                        & Q(
                            Q(data__lte=start_date, data_fim__gte=start_date)
                            | Q(data__gte=start_date, data__lte=end_date)
                        )
                    )
                    | Q(
                        Q(data__isnull=False, data_fim__isnull=True)
                        & Q(data__lte=start_date)
                    )
                )
            )

        try:
            inc_progress = 100.0 / query.count()
        except ZeroDivisionError:
            inc_progress = 1

        for falta in query:
            group_job.append(
                atribuir_comp_desc.s(
                    task.uuid,
                    inc_progress,
                    falta.id,
                    reference,
                    user,
                    competencia_desconto,
                )
            )

        result = None
        job = group(group_job)

        result = job.apply_async()
        while not result.ready():
            time.sleep(2)

        state = "ready"
        message = f"<p>Concluído - Atribuição de Competência de Desconto."
    except Exception as err:
        log.error(err)
        state = "failed"
        message = f"<p>Erro ao Atribuir Competência de Desconto</p>"
        task.info(msg=f"<p>Erro ao Atribuir Competência de Desconto</p>", type_of=3)

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def atribuir_comp_desc_por_falta_task(
    task, hook, user, falta_ids, competencia_desconto
):
    """
    Esta Task é responsável por atribuir Competência de Desconto às faltas do Gestor de Faltas
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
    task = Task.objects.get(uuid=task)
    set_current_user(user)
    feedback("", 0, message=f"<p>Atribuindo Competência de Desconto</p>", state=state)
    task.info(
        msg=f"Iniciando atribuição - {time.strftime('%d/%m/%Y %H:%M:%S')}", type_of=1
    )

    try:
        group_job = []

        q_faltas = Falta.objects.filter(pk__in=falta_ids)

        try:
            inc_progress = 100.0 / q_faltas.count()
        except ZeroDivisionError:
            inc_progress = 1

        for falta in q_faltas:
            reference = f"{falta.data.month/falta.data.year}"
            group_job.append(
                atribuir_comp_desc.s(
                    task.uuid,
                    inc_progress,
                    falta.id,
                    reference,
                    user,
                    competencia_desconto,
                )
            )

        result = None
        job = group(group_job)

        result = job.apply_async()
        while not result.ready():
            time.sleep(2)

        state = "ready"
        message = f"<p>Concluído - Atribuição de Competência de Desconto."
    except Exception as err:
        log.error(err)
        state = "failed"
        message = f"<p>Erro ao Atribuir Competência de Desconto</p>"
        task.info(msg=f"<p>Erro ao Atribuir Competência de Desconto</p>", type_of=3)

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def atribuir_comp_desc(
    task_uuid, inc_progress, falta_id, reference, user_id, competencia_desconto
):
    task = Task.objects.get(uuid=task_uuid) if task_uuid else None
    set_current_user(user_id)

    falta = Falta.objects.filter(Q(id=falta_id) & Q(situacao=1))
    try:
        falta.update(competencia_desconto=competencia_desconto)
    except Exception as e:
        if task:
            task.info(msg=f"Erro: {e} ao Atribuir Competência de Desconto", type_of=3)

    if task:
        Task.objects.filter(pk=task.pk).update(progress=F("progress") + inc_progress)
