# -*- coding: utf-8 -*-
import os
import time
from logging import getLogger

from celery import Celery, group
from datetime import datetime, timedelta

from contrib.daterange import NewDateRange
from contrib.middleware import set_current_user, get_current_user
from contrib.utils import DateUtils
from engine.mq.models import Task
from dateutil.relativedelta import relativedelta
from rh.dayoff.models import AcquisitionPeriod, GroupPeriod, Activity, Configuration
from rh.dayoff.const import (
    ACQP_WAIT,
    CONF_ELECTORAL_SLACK,
    AUTO_HOMOLOGATION_AFTER_SCALE,
    ACQP_PROGRESS,
    CONF_BIRTHDAY_BREAK,
    CONF_RECESS,
)
from rh.dayoff.const import (
    ACQP_CREATION_ERROR,
    ACQP_CREATION_UPDATED,
    ACQP_CREATION_CREATED,
)
from rh.afastamento.models import FolgaEleitoral
from rh.models import Servidor
from django.db.models import Q
from engine.notification.models import Notification

import json


log = getLogger(__name__)

app = Celery("dayoff")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task()
def homologate(
    task,
    hook,
    group,
    acquisition_period,
    activity,
    homologation_date,
    publication_date,
    attachment,
    scale_homologation,
    context,
    user,
    success,
):
    """Este método é responsável pela tarefa de homologação.

    Args:
        group (int): instância de período aquisitivo
        attachment (int): pk do anexo
    Returns:
        action (ActivityHomologate): uma instância de ação válida
    Raise:
        Exception: raise exception quando não passa pela validação
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

    has_exception = None
    try:
        set_current_user(user)

        acquisition_periods = AcquisitionPeriod.objects.none()
        if group:
            acquisition_periods = AcquisitionPeriod.objects.filter(
                group_period__pk=group
            )
        elif acquisition_period:
            acquisition_periods = AcquisitionPeriod.objects.filter(
                pk__in=acquisition_period
            )
        elif activity:
            acquisition_periods = AcquisitionPeriod.objects.filter(
                activities__pk__in=activity
            )
        else:
            raise Exception("Nada informado para homologar.")

        aq = acquisition_periods.first()

        message = "<p>%s - Homologando %s...</p>" % (
            aq.configuration.get_type_of_usufruct_display(),
            aq.group_period,
        )
        feedback("", 0, message=message, state=state)
        task.info(
            msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )

        AcquisitionPeriod.run_batch_homologation(
            group=group,
            acquisition_period=acquisition_period,
            activity=activity,
            homologation_date=homologation_date,
            publication_date=publication_date,
            attachment=attachment,
            scale_homologation=scale_homologation,
            context=context,
            user=user,
            task=task,
        )

        state = "ready"
        message = f"<p>A Homologação do {acquisition_periods.first().group_period} foi finalizada.</p>"
        task.info(
            msg=f"Finalizando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )

    except Exception as err:
        log.exception(err)
        state = "failed"
        has_exception = err
        message = f"<p>DAYOFF - Falha na homologação.</p><p>{err}</p>"
        task.info(msg=message, type_of=3)

    task.message = message
    task.finish_execution(status=state, msg=message)

    if has_exception:
        raise has_exception


@app.task()
def run_release(task, hook, group_id, user):
    """Este método é responsável pela tarefa de liberar o período aquisitivo para marcação.

    Args:
        group_id (int): id do GroupPeriod
        user (int): Usuário responsável por executar a ação
    Returns:
        activity: ação executada
    Raise:
        Exception: raise exception quando não passa pela validação
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

    has_exception = None
    try:
        set_current_user(user)

        group_ = GroupPeriod.objects.get(id=group_id)
        today = datetime.now().date()

        if group_.start_date_book and (today < group_.start_date_book):
            group_.start_date_book = today
            group_.save()

        acquisition_periods = AcquisitionPeriod.objects.filter(
            group_period__pk=group_.id, status__in=[ACQP_WAIT]
        )

        message = f"<p>Liberando marcação do {group_}"
        feedback("", 0, message=message, state=state)
        task.info(
            msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )

        inc_progress = (
            (100.0 / acquisition_periods.count()) if acquisition_periods else 100.0
        )

        result = None
        job = group(
            [
                _process_batch_release.s(
                    task.uuid, ap.id, user, inc_progress=inc_progress
                )
                for ap in acquisition_periods
            ]
        )

        result = job.apply_async()

        while not result.ready():
            time.sleep(2)

        state = "ready"
        message = f"<p>A marcação do {group_} foi liberada.</p>"

        task.info(
            msg=f"Finalizando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )

    except Exception as err:
        log.exception(err)
        state = "failed"
        has_exception = err
        message = f"<p>DAYOFF - Falha na liberação para marcação.</p><p>{err}</p>"
        task.info(msg=message, type_of=3)

    task.message = message
    task.finish_execution(status=state, msg=message)

    if has_exception:
        raise has_exception


@app.task()
def _process_batch_release(task_uuid, acquisition_period_id, user, inc_progress=1):
    set_current_user(user)

    task = Task.objects.filter(uuid=task_uuid).first()

    acquisition_period = AcquisitionPeriod.objects.get(pk=acquisition_period_id)

    try:
        acquisition_period.release()
    except Exception as e:
        log.debug(e)
        message = f"O Período aquisitivo {acquisition_period} não foi liberado. ({e})"
        task.info(msg=message, type_of=3)

    if task:
        task.increment_progress(inc_progress)


@app.task()
def generate_all_acquisition_periods(
    task, hook, group_, create_or_update, user, success
):
    """Este task chama geração de Períodos Aquisitivos."""

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

    has_exception = None
    try:
        set_current_user(user)
        today = datetime.today()

        filename = "criação_períodos_aquisitivos_%s.txt" % (
            datetime.strftime(today, "%d_%m_%Y_%H_%M")
        )

        task.data = json.dumps({"filename": filename})
        task.save()

        group_ = GroupPeriod.objects.get(pk=group_)
        log.info(group_)

        message = f"<p>Criando Períodos Aquisitivos de {group_}...</p>"
        feedback("", 0, message=message, state=state)
        task.info(
            msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )

        group_.run_generate_all_acquisition_periods(task.uuid, create_or_update)

        state = "ready"
        message = f"<p>Os períodos aquisitivos do grupo {group_} foram criados ou atualizados .</p>"
        task.info(
            msg=f"Finalizando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )

    except Exception as err:
        log.exception(err)
        state = "failed"
        has_exception = err
        message = (
            f"<p>DAYOFF - Falha na criação de Períodos Aquisitivos.</p><p>{err}</p>"
        )
        task.info(msg=message, type_of=3)

    task.message = message
    task.finish_execution(status=state, msg=message)

    if has_exception:
        raise has_exception


@app.task()
def run_upgrade_aquisition_period(
    task, hook, acquisition_periods, update_usufructs, user, success
):
    """Esta task chama atualização de Períodos Aquisitivos.

    Args:
        acquisition_periods (list): []
        update_usufructs (bool): False
        user (pk):

    Raise:
        Exception: raise exception quando não passa pela validação
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

    has_exception = None
    try:
        set_current_user(user)
        today = datetime.today()

        filename = "atualização_períodos_aquisitivos_%s.txt" % (
            datetime.strftime(today, "%d_%m_%Y_%H_%M")
        )

        task.data = json.dumps({"filename": filename})
        task.save()

        acqps = AcquisitionPeriod.objects.filter(pk__in=acquisition_periods)
        log.info(acqps)
        total = acqps.count()
        if total == 1:
            message = f"<p>Atualizando Períodos Aquisitivos ({acqps.first()})...</p>"
        else:
            message = f"<p>Atualizando ({total}) Períodos Aquisitivos...</p>"
        feedback("", 0, message=message, state=state)
        task.info(
            msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )

        for acqp in acqps:
            acqp.upgrade_aquisition_period(task=task, update_usufructs=update_usufructs)

        state = "ready"
        if total == 1:
            message = f"<p>Período Aquisitivo ({acqps.first()}) atualizado.</p>"
        else:
            message = f"<p>Períodos Aquisitivos ({total}).</p>"
        task.info(
            msg=f"Finalizando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )

    except Exception as err:
        log.exception(err)
        state = "failed"
        has_exception = err
        message = (
            f"<p>DAYOFF - Falha na criação de Períodos Aquisitivos.</p><p>{err}</p>"
        )
        task.info(msg=message, type_of=3)

    task.message = message
    task.finish_execution(status=state, msg=message)

    if has_exception:
        raise has_exception


@app.task()
def authorize(
    task,
    hook,
    authorize,
    attachment,
    note,
    activity,
    immediate_authorization,
    mediate_authorization,
    context,
    user,
):
    """Este método é responsável pela tarefa de autorizar as atividades.

    Args:
        authorize (bool): campo indicando se houve autorização, True-Sim, False-Não, None-não realizado
        attachment (Attachment): anexo informado
        note (bool): anotar
        activity (int): Activity pk
        immediate_authorization(Servidor): chefe imediato
        mediate_authorization(Servidor): chefe mediato
        context(str): indicação se foi feito no window(restful) de admin, immediate, mediate, employee
    """

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    activity = activity if activity else []

    state = "progress"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)

        today = datetime.now().date()

        message = f"<p>Autorizando atividades."
        feedback("", 0, message=message, state=state)
        task.info(
            msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )

        inc_progress = (100.0 / len(activity)) if activity else 100.0

        result = None
        job = group(
            [
                _process_batch_authorize.s(
                    task.uuid,
                    act,
                    authorize,
                    mediate_authorization,
                    immediate_authorization,
                    attachment,
                    note,
                    context,
                    user,
                    inc_progress=inc_progress,
                )
                for act in activity
            ]
        )

        result = job.apply_async()

        while not result.ready():
            time.sleep(2)

        state = "ready"
        message = f"<p>O processo de autorização foi finalizado.</p>"

        task.info(
            msg=f"Finalizando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )

    except Exception as err:
        log.exception(err)
        state = "failed"
        has_exception = err
        message = f"<p>DAYOFF - Falha na autorização.</p><p>{err}</p>"
        task.info(msg=message, type_of=3)

    task.message = message
    task.finish_execution(status=state, msg=message)

    if has_exception:
        raise has_exception


@app.task()
def _process_batch_authorize(
    task_uuid,
    activity_id,
    authorize,
    mediate_authorization,
    immediate_authorization,
    attachment,
    note,
    context,
    user,
    inc_progress=1,
):
    set_current_user(user)

    task = Task.objects.filter(uuid=task_uuid).first()

    activity = Activity.objects.get(pk=activity_id)

    try:
        activity.authorize_and_homologate(
            authorize=authorize,
            mediate_authorization=mediate_authorization,
            immediate_authorization=immediate_authorization,
            attachment=attachment,
            note=note,
            context=context,
        )
    except Exception as err:
        log.exception(err)
        message = f"A atividade {activity} não foi autorizada. ({err})"
        task.info(msg=message, type_of=3)

    if task:
        task.increment_progress(inc_progress)


@app.task()
def call_run_generate_periods_task(task, hook, employee, date_reference, user, success):
    """Este task chama geração de Períodos Aquisitivos."""

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

    has_exception = None
    try:
        set_current_user(user)

        today = datetime.today()

        filename = "criação_períodos_aquisitivos_%s.txt" % (
            datetime.strftime(today, "%d_%m_%Y_%H_%M")
        )
        task.data = json.dumps({"filename": filename})

        dt_reference = DateUtils.str_to_date(date_reference)
        employee_ = Servidor.objects.get(pk=employee)
        message = f"<p>Criação/Atualização de Período Aquisitivo de {employee_}...</p>"
        feedback("", 0, message=message, state=state)
        task.info(
            msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )

        # query_base = GroupPeriod.objects.filter(
        #     configuration__type_of_usufruct__in=[CONF_BIRTHDAY_BREAK, CONF_RECESS],
        #     configuration__type_employees__cvalue=employee_.type_by_possession,
        # ).filter(year_reference__gte=(dt_reference - relativedelta(years=1)).year)

        query_base = GroupPeriod.objects.filter(
            configuration__run_signal=True,
            configuration__type_employees__cvalue=employee_.type_by_possession,
        ).filter(year_reference__gte=(dt_reference - relativedelta(years=1)).year)
        _diff = False
        msg_notify = ""
        for group_ in query_base:
            _klass = group_.classcode.cls
            class_code_acqp = _klass(group_, employee_)

            # FIXME: definir como serão criados os recessos legados

            error = None
            try:
                acqp, mode = class_code_acqp.update_or_create_acquisition_period()
            except Exception as err:
                log.exception(err)
                error = err
                _diff = True

            if error:
                task.info(
                    msg=f"Erro ao criar/atualizar período {group_} \n{error}", type_of=3
                )
                msg_notify += f"Erro ao criar/atualizar período {group_} \n{error}\n"
            elif mode == ACQP_CREATION_UPDATED:
                if acqp.diff:
                    _diff = True
                    _message = ""
                    if acqp.diff.get("pendency"):
                        _pendency_new = "Sim" if acqp.diff.get("pendency")[1] else "Não"
                        _message = f"Com pendência: {_pendency_new}\n"
                    if acqp.diff.get("days"):
                        _message = f"{_message}Quantidade de dias mudou de {acqp.diff.get('days')[0]} para {acqp.diff.get('days')[1]}\n"
                    if acqp.diff.get("info") and acqp.diff.get("info")[1]:
                        _message = f"{_message}Info: {acqp.diff.get('info')[1]}\n"

                    if _message:
                        _message = f"Período aquisitivo ({acqp}) atualizado\n{_message}"
                        msg_notify += _message
                        task.info(msg=_message, type_of=2)
                elif acqp.info:
                    task.info(
                        msg=f"Período aquisitivo ({acqp}) atualizado: {acqp.info}",
                        type_of=2,
                    )
            elif mode == ACQP_CREATION_CREATED:
                task.info(msg=f"Período aquisitivo ({acqp}) criado!", type_of=1)
                msg_notify += f"Período aquisitivo ({acqp}) criado!\n"
                _diff = True
            else:
                task.info(msg=f"{mode}: {acqp}", type_of=2)

        state = "ready"
        msg_params = locals()
        msg_params.update(employee=f"{employee_}")
        message = success % msg_params
        task.info(
            msg=f"Finalizando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )

    except Exception as err:
        log.exception(err)
        state = "failed"
        has_exception = err
        message = f"<p>DAYOFF - Falha na criação de Períodos Aquisitivos do {Servidor.objects.get(pk=employee)}.</p><p>{err}</p>"
        task.info(msg=message, type_of=3)

    task.message = message
    task.state = state
    task.finish_execution(status=state, msg=message)
    if not _diff:
        task.mark_finished()
    elif _diff and user == "athenas":
        query = Servidor.objects.filter(
            Q(user__user_permissions__codename="dayoff_notify_admin")
            | Q(user__groups__permissions__codename="dayoff_notify_admin")
        ).distinct()
        for emp in query:
            Notification.notify("DAYOFF-NOTIFY-ADMIN", emp, msg=msg_notify)

    if has_exception:
        raise has_exception


@app.task()
def call_acquisition_manager(task, hook, employee, start_date, end_date, user, success):
    """Este task chama geração de AcquisitionPeriod.acquisition_manager."""

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

    has_exception = None
    try:
        set_current_user(user)
        today = datetime.today()

        start_date = DateUtils.str_to_date(start_date)
        end_date = DateUtils.str_to_date(end_date) if end_date else None
        filename = "atualização_períodos_aquisitivos_%s.txt" % (
            datetime.strftime(today, "%d_%m_%Y_%H_%M")
        )
        task.data = json.dumps({"filename": filename})

        employee_ = Servidor.objects.get(pk=employee)
        message = f"<p>Criação/Atualização de Período Aquisitivo de {employee_}...</p>"
        feedback("", 0, message=message, state=state)
        task.info(
            msg=f"Iniciando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )
        _diff = []
        for group in GroupPeriod.objects.filter(acquisitionperiods__employee=employee_):
            if group.classcode:
                if group.classcode.cls(
                    group_period=group, employee=employee_
                ).acquisition_manager(
                    start_date=start_date, end_date=end_date, task=task
                ):
                    _diff.append(group.pk)

        state = "ready"
        msg_params = locals()
        msg_params.update(employee=f"{employee_}")
        message = success % msg_params
        task.info(
            msg=f"Finalizando processamento - {time.strftime('%d/%m/%Y %H:%M:%S')}",
            type_of=1,
        )

    except Exception as err:
        log.exception(err)
        state = "failed"
        has_exception = err
        message = f"<p>DAYOFF - Falha na criação de Períodos Aquisitivos do {Servidor.objects.get(pk=employee)}.</p><p>{err}</p>"
        task.info(msg=message, type_of=3)

    task.message = message
    task.state = state
    task.finish_execution(status=state, msg=message)
    if not _diff:
        task.mark_finished()
    elif _diff and user == "athenas":
        msg_notify = (
            "Houve alteração nos períodos aquisitivos do servidor: %s" % employee_
        )
        query = Servidor.objects.filter(
            Q(user__user_permissions__codename="dayoff_notify_admin")
            | Q(user__groups__permissions__codename="dayoff_notify_admin")
        ).distinct()
        for emp in query:
            Notification.notify("DAYOFF-NOTIFY-ADMIN", emp, msg=msg_notify)

    if has_exception:
        raise has_exception
