# -*- coding: utf-8 -*-

import os
import time

import django
from celery import Celery, group
from django.db.models import Max, Q

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from engine.mq.models import Task
from rh.gfp.dirf.models import DEBUG_EMPLOYES, DEBUG_PERSONS, Dialect, DirfSummary
from rh.models import Servidor

log = getLogger("gfp")
app = Celery("gfp")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)
django.setup()


@app.task()
def summarize_employee(task_uuid, dialect_id, employee_id, user, inc_progress=1):
    set_current_user(user)

    task = Task.objects.filter(uuid=task_uuid).first()
    dialect = Dialect.objects.get(pk=dialect_id)
    employee = Servidor.objects.get(pk=employee_id)

    dialect.summarize_employee(employee)
    log.debug(">>> FINALIZADO for %s" % employee)

    if task:
        task.info(f"{employee.pessoa_fisica} avaliado!")
        task.increment_progress(inc_progress)


@app.task()
def summarize_dirf_by_dialect(
    task, hook, dialect_id, user, receipt_number=None, clear=False
):

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    state = "progress"
    dialect = Dialect.objects.get(pk=dialect_id)
    message = "<p>Erro ao sumarizar DIRF %s</p>" % dialect
    task = Task.objects.get(uuid=task)
    # dr = NewDateRange.from_month(dialect.periodo.ano, min(dialect.periodo.mes, 12))

    log.debug("TASK %s" % task.uuid)

    try:
        set_current_user(user)
        feedback("", 0, message="<p>Sumarizando DIRF - %s</p>" % dialect, state=state)
        task.info(
            msg="Iniciando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
            type_of=1,
        )

        q_employeers = Servidor.objects.filter(
            (
                Q(
                    entries__contracheque__folha__dt_pagamento__year=dialect.calendar_year
                )
                | Q(
                    entries__reference_month=13,
                    entries__reference_year=dialect.calendar_year,
                )
            )
        ).distinct()

        debug_persons_ids = DEBUG_PERSONS + [
            e.pessoa_fisica.id
            for e in Servidor.objects.filter(matricula__in=DEBUG_EMPLOYES)
        ]

        if debug_persons_ids:
            q_employeers = q_employeers.filter(pessoa_fisica__in=debug_persons_ids)

        if clear:
            task.info("Apagando sumários da %s!" % dialect)
            q_summaries = DirfSummary.objects.filter(
                calendar_year=dialect.calendar_year, dirf_created=True
            )
            if debug_persons_ids:
                q_summaries = q_summaries.filter(person__in=debug_persons_ids)
            q_summaries.delete()

        # Procurando por pessoas fisicas repetidas -------------------------
        persons = []
        exclude_employees = []
        for employee in q_employeers:
            if employee.pessoa_fisica.pk in persons:
                exclude_employees.append(employee.pk)
            persons.append(employee.pessoa_fisica.pk)
        q_employeers = q_employeers.exclude(pk__in=exclude_employees)
        # ------------------------------------------------------------------

        total_employees = q_employeers.count()
        inc_progress = 100.0 / total_employees
        log.debug("TASK %s - Increment: %0.1f" % (task.uuid, inc_progress))

        result = None
        job = group(
            [
                summarize_employee.s(
                    task.uuid, dialect.pk, employee.pk, user, inc_progress=inc_progress
                )
                for employee in q_employeers
            ]
        )

        log.debug("TASK %s - Iniciando job" % task.uuid)
        result = job.apply_async()
        log.debug("TASK %s - Job iniciado" % task.uuid)

        while not result.ready():
            time.sleep(2)

        log.debug("TASK %s - Iniciando job 2" % task.uuid)

        result = DirfSummary.objects.filter(
            calendar_year=dialect.calendar_year, dirf_created=True
        ).aggregate(date=Max("modified_at"))
        dialect.last_processed_summary = result["date"]
        dialect.save()

        # Gerando arquivo da DIRF ------------------------------------
        dialect.generate_file(receipt_number=receipt_number, task=task)

        state = "ready"
        message = "<p>Sumarização da <b>%s</b> concluída</p>" % dialect
        task.info(
            msg="Finalizando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
            type_of=1,
        )

        log.debug("TASK %s - Iniciando job 3" % task.uuid)

    except Exception as err:
        log.exception(err)
        state = "failed"
        # message = u'<p>Erro ao avaliar diferenças</p>'
        task.info(msg=message, type_of=3)

    task.finish_execution(status=state, msg=message)
    # feedback('', 100)
    # task.message = message
    # task.state = state
    # task.save()
