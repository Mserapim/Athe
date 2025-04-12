# -*- coding: utf-8 -*-


from logging import getLogger
from celery import Celery, group
from django.db.models import F
from dateutil.relativedelta import relativedelta
from contrib.utils import DateUtils
from contrib.middleware import set_current_user
from datetime import datetime
from django.db.models import Q
from engine.mq.models import Task
from rh.models import (
    EmployeeHoursWorkContractWorkload,
    HoursWorkContractWorkload,
    HoursWorkContract,
    Servidor,
)
from rh.scripts.atualizar_carga_horaria import (
    atualizar_carga_servidor,
    criar_carga_servidor,
)

import os


log = getLogger(__name__)

app = Celery("hoursworkcontractworkload")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task()
# def apply_employee_workload(task, hook, hwc_workload_origin, hwc_workload_destiny, date_start, date_end, employees, reapply, user):
def apply_employee_workload(
    task,
    hook,
    hwc_workload_origin,
    hwc_workload_destiny,
    date_start,
    date_end,
    locality,
    workplace,
    all_employee,
    reapply,
    user,
    success,
):
    state = "failed"
    message = "<p>RH - Aplicando Escalas...</p>"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.save()

        employees = Servidor.objects.filter(Q(ativo=True) & Q(tipo="S"))
        if not all_employee:
            if locality:
                employees = employees.filter(
                    servidor_lotacao__lotacao__localidade__pk=int(locality),
                    servidor_lotacao__ativo=True,
                )
            if workplace:
                employees = employees.filter(
                    servidor_lotacao__lotacao__pk=int(workplace),
                    servidor_lotacao__ativo=True,
                )

            if not locality and not workplace:
                employees = Servidor.objects.filter(
                    pk__in=EmployeeHoursWorkContractWorkload.objects.filter(
                        hours_work_contract_workload__pk=int(hwc_workload_origin)
                    ).values("employee"),
                    ativo=True,
                )

        employees = [emp.pk for emp in employees]

        task_destiny = Task.start(
            _apply,
            hwc_workload=hwc_workload_destiny,
            date_start=date_start,
            date_end=date_end,
            employees=employees,
            user=user,
            task_father=task.pk,
        )

        while Task.objects.get(uuid=task_destiny.uuid).state in (
            "initializing",
            "initialized",
            "progress",
        ):
            pass

        if reapply and date_end:
            if type(hwc_workload_origin) is int:
                hwc_workload_origin = HoursWorkContractWorkload.objects.get(
                    pk=hwc_workload_origin
                )
            date_start = DateUtils.str_to_date(date_end) + relativedelta(days=1)
            task_origin = Task.start(
                _apply,
                hwc_workload=hwc_workload_origin.pk,
                date_start=DateUtils.date_to_str(date_start),
                date_end=None,
                employees=employees,
                user=user,
                task_father=task.pk,
            )

            while Task.objects.get(uuid=task_origin.uuid).state in (
                "initializing",
                "initialized",
                "progress",
            ):
                pass

        deadline = (datetime.now().date() + relativedelta(days=2)).strftime("%d/%m/%Y")
        msg_params = locals()
        msg_params.update(deadline=deadline)
        msg_params.update(uuid=task.uuid)
        message = success % msg_params

        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>RH - Aplicando Escalas. Falha na criação.</p><p>%s</p>" % err

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def _apply(
    task, hook, hwc_workload, date_start, date_end, employees, user, task_father
):
    state = "failed"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    description = "de %s a %s" % (date_start, date_end if date_end else "----")

    has_exception = None
    try:
        set_current_user(user)

        task.message = "<p>RH - Aplicando Escala %s %s...</p>" % (
            HoursWorkContractWorkload.objects.get(pk=hwc_workload),
            description,
        )
        task.state = "progress"
        task.save()

        EmployeeHoursWorkContractWorkload._apply(
            hwc_workload,
            date_start,
            date_end=date_end,
            employees=employees,
            task=task_father,
        )

        message = "<p>RH - Aplicando Escala %s %s finalizado.</p>" % (
            HoursWorkContractWorkload.objects.get(pk=hwc_workload),
            description,
        )
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>RH - Aplicando Escala %s %s. Falha na criação.</p><p>%s</p>" % (
            HoursWorkContractWorkload.objects.get(pk=hwc_workload),
            description,
            err,
        )

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def atualizar_carga_horaria_task(task, user, servidor_ids, inc_progress=0):
    """
    Esta Task é responsável atualizar as carga horárias
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
    msg = f"<p>Erro ao atualizar a carga horaria.</p>"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback("", 0, message=f"<p>Atualizando carga horária.</p>", state=state)

    try:
        for servidor_id in servidor_ids:
            atualizar_carga_servidor(servidor_id)

        state = "ready"
        message = f"<p>Atualização da carga horária concluída."
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
def atualizar_carga_horaria_batch_task(task, hook, user):
    task = Task.objects.get(uuid=task)
    task.message = "<p>Atualizando carga horária...</p>"
    task.state = "progress"
    task.save()

    servidores = Servidor.objects.filter(exercise_date__isnull=False).exclude(
        type_by_possession__in=[
            "MBR",
            "MEC",
            "MAP",
            "SAP",
            "BFP",
            "TCR",
            "APO",
            "COE",
            "XXX",
            "JCA",
        ]
    )

    total = servidores.count()
    inc_progress = 100.0 / total if total else 0

    batch_size = 10
    servidores_ids = []
    jobs = []

    for servidor in servidores.iterator():
        servidores_ids.append(servidor.pk)
        if len(servidores_ids) == batch_size:
            jobs.append(
                atualizar_carga_horaria_task.s(
                    task.uuid, user, servidores_ids, inc_progress=inc_progress
                )
            )
            servidores_ids = []

    if servidores_ids:
        jobs.append(
            atualizar_carga_horaria_task.s(
                task.uuid, user, servidores_ids, inc_progress=inc_progress
            )
        )

    job = group(jobs)

    job.apply_async()

    task.info(pct_progress=0)
    task.finish_execution(set_process=False)


@app.task()
def criar_carga_horaria_task(task, user, servidor_ids, inc_progress=0):
    """
    Esta Task é responsável criar as carga horárias do servidor
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
    msg = f"<p>Erro ao criar a carga horaria.</p>"
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback("", 0, message=f"<p>Criando carga horária.</p>", state=state)

    try:
        jornadas_servidor = HoursWorkContract.objects.filter(code__in=["1", "3"])
        jornada_residentes = HoursWorkContract.objects.get(code="3")
        jornadas_estagiarios = HoursWorkContract.objects.filter(code__in=["6", "4"])

        for servidor_id in servidor_ids:
            servidor = Servidor.objects.get(pk=servidor_id)
            if servidor.type_by_possession == "RES":
                criar_carga_servidor(servidor, jornada_residentes)
            elif servidor.type_by_possession == "EST":
                for jornada in jornadas_estagiarios:
                    criar_carga_servidor(servidor, jornada)
            else:
                for jornada in jornadas_servidor:
                    criar_carga_servidor(servidor, jornada)

        state = "ready"
        message = f"<p>Criação da carga horária concluída."
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
def criar_carga_horaria_batch_task(task, hook, user):
    task = Task.objects.get(uuid=task)
    task.message = "<p>Criando carga horária...</p>"
    task.state = "progress"
    task.save()

    servidores = Servidor.objects.filter(exercise_date__isnull=False).exclude(
        type_by_possession__in=[
            "MBR",
            "MEC",
            "MAP",
            "SAP",
            "BFP",
            "TCR",
            "APO",
            "COE",
            "XXX",
            "JCA",
        ]
    )

    total = servidores.count()
    inc_progress = 100.0 / total if total else 0

    batch_size = 5
    servidores_ids = []
    jobs = []

    for servidor in servidores.iterator():
        servidores_ids.append(servidor.pk)
        if len(servidores_ids) == batch_size:
            jobs.append(
                criar_carga_horaria_task.s(
                    task.uuid, user, servidores_ids, inc_progress=inc_progress
                )
            )
            servidores_ids = []

    if servidores_ids:
        jobs.append(
            criar_carga_horaria_task.s(
                task.uuid, user, servidores_ids, inc_progress=inc_progress
            )
        )

    job = group(jobs)

    job.apply_async()

    task.info(pct_progress=0)
    task.finish_execution(set_process=False)
