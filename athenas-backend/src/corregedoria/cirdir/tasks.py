# -*- coding: utf-8 -*-
import os
import json
import time
import django

from subprocess import call, Popen, PIPE
from celery import Celery, group
from django.conf import settings
from contrib.utils import getLogger
from standard.models import Configuration
from datetime import datetime, timedelta
from decimal import *
from contrib.middleware import set_current_user
from engine.mq.models import Task
from django.template.defaultfilters import slugify
from django.db.models.query_utils import Q
from django.forms.models import model_to_dict
from corregedoria.cirdir.models import *
from rh.models import *


log = getLogger("tasker")
app = Celery("celerysrdir")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task()
def add_newyear(
    task, hook, newyear, lastyear, address, teaching, property, debits, health, user
):
    state = "failed"
    message = "<b>SRDIR</b>: Erro ao adicionar novo ano"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        initial_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        set_current_user(user)
        message = "<b>SRDIR</b>: Adicionando novo ano...<br /><ul><li>%s</li></ul>" % (
            ("Ano: <b>" + str(newyear) + "</b>")
        )
        task.message = message
        task.state = "ready"
        task.save()
        task.info(msg="Iniciando...", pct_progress=0.001)
        list_of_employees = Servidor.objects.filter(ativo=True).filter(
            tipo__in=["S", "M"]
        )
        inc_progress = 100.0 / list_of_employees.count()
        rst = False
        fail = False
        result = None
        job = group(
            [
                add_newyear_employee.s(
                    membro.matricula,
                    newyear,
                    lastyear,
                    address,
                    teaching,
                    property,
                    debits,
                    health,
                    user,
                    task_father=task.uuid,
                    inc_progress=inc_progress,
                )
                for membro in list_of_employees
            ]
        )
        result = job.apply_async()
        while not (rst):
            rst = result.ready() if result else True
            time.sleep(1)
        fail = result.failed() if result else False
        if not (fail):
            state = "ready"
            final_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            message = (
                "<b>SRDIR</b>: Adição concluída com sucesso!<br /><ul><li>%s</li></ul>"
                % (("Ano: <b>" + str(newyear) + "</b>"))
            )
        else:
            state = "failed"
            message = "<b>SRDIR</b>: Erro ao adicionar novo ano"
        task.finish_execution(msg=message)
    except Exception as err:
        log.exception(str(err))
        has_exception = err
        state = "failed"
        message = "<b>SRDIR</b>: Erro ao adicionar novo ano"
        task.finish_execution(msg=message, status="ERROR")
    if has_exception:
        raise str(has_exception)


@app.task()
def add_newyear_employee(
    membro,
    newyear,
    lastyear,
    address,
    teaching,
    property,
    debits,
    health,
    user,
    task_father=None,
    inc_progress=0,
):
    has_exception = None
    try:
        set_current_user(user)
        employee = Servidor.objects.filter(matricula=membro).first()
        if ControlInformation.objects.filter(employee=employee, year=newyear).exists():
            if task_father:
                task = Task.objects.get(uuid=task_father)
                task.info(
                    "Não realizado: MP%s - %s<br /><b>SRDIR</b> já existe!"
                    % (str(membro), employee.pessoa_fisica.nome),
                    pct_progress=Decimal(inc_progress),
                )
        else:
            if task_father:
                task = Task.objects.get(uuid=task_father)
                task.info(
                    "Iniciando: MP%s - %s" % (str(membro), employee.pessoa_fisica.nome)
                )

            if len(lastyear) > 0:
                controlinformation = ControlInformation.objects.filter(
                    employee=employee, year=lastyear
                ).first()
                previous_pk = controlinformation.pk if controlinformation else None
                if controlinformation:
                    controlinformation.pk = None
                else:
                    controlinformation = ControlInformation()
                    controlinformation.employee = employee
                controlinformation.year = newyear
                controlinformation.previous_controlinformation_id = previous_pk
                cfg = Configuration.get_or_create("corregedoria")
                controlinformation.open_date_address = datetime(
                    int(newyear),
                    int(cfg.get("var_open_date_address").split("/")[1]),
                    int(cfg.get("var_open_date_address").split("/")[0]),
                )
                controlinformation.close_date_address = datetime(
                    int(newyear),
                    int(cfg.get("var_close_date_address").split("/")[1]),
                    int(cfg.get("var_close_date_address").split("/")[0]),
                )
                controlinformation.open_date_teaching_1st_semestry = datetime(
                    int(newyear),
                    int(cfg.get("var_open_date_teaching_1st_semestry").split("/")[1]),
                    int(cfg.get("var_open_date_teaching_1st_semestry").split("/")[0]),
                )
                controlinformation.close_date_teaching_1st_semestry = datetime(
                    int(newyear),
                    int(cfg.get("var_close_date_teaching_1st_semestry").split("/")[1]),
                    int(cfg.get("var_close_date_teaching_1st_semestry").split("/")[0]),
                )
                controlinformation.open_date_teaching_2nd_semestry = datetime(
                    int(newyear),
                    int(cfg.get("var_open_date_teaching_2nd_semestry").split("/")[1]),
                    int(cfg.get("var_open_date_teaching_2nd_semestry").split("/")[0]),
                )
                controlinformation.close_date_teaching_2nd_semestry = datetime(
                    int(newyear),
                    int(cfg.get("var_close_date_teaching_2nd_semestry").split("/")[1]),
                    int(cfg.get("var_close_date_teaching_2nd_semestry").split("/")[0]),
                )
                controlinformation.open_date_property = datetime(
                    int(newyear),
                    int(cfg.get("var_open_date_property").split("/")[1]),
                    int(cfg.get("var_open_date_property").split("/")[0]),
                )
                controlinformation.close_date_property = datetime(
                    int(newyear),
                    int(cfg.get("var_close_date_property").split("/")[1]),
                    int(cfg.get("var_close_date_property").split("/")[0]),
                )
                controlinformation.open_date_debits = datetime(
                    int(newyear),
                    int(cfg.get("var_open_date_debits").split("/")[1]),
                    int(cfg.get("var_open_date_debits").split("/")[0]),
                )
                controlinformation.close_date_debits = datetime(
                    int(newyear),
                    int(cfg.get("var_close_date_debits").split("/")[1]),
                    int(cfg.get("var_close_date_debits").split("/")[0]),
                )
                controlinformation.open_date_health = datetime(
                    int(newyear),
                    int(cfg.get("var_open_date_health").split("/")[1]),
                    int(cfg.get("var_open_date_health").split("/")[0]),
                )
                controlinformation.close_date_health = datetime(
                    int(newyear),
                    int(cfg.get("var_close_date_health").split("/")[1]),
                    int(cfg.get("var_close_date_health").split("/")[0]),
                )
                controlinformation.closed_address = False
                controlinformation.closed_teaching_1st_semestry = False
                controlinformation.closed_teaching_2nd_semestry = False
                controlinformation.closed_property = False
                controlinformation.closed_debits = False
                controlinformation.closed_health = False
                controlinformation.nusubmit()
                controlinformation.save(saving=False)
                if address:
                    controlinformation.copy_address_from(previous_pk)

                if teaching:
                    controlinformation.copy_teaching_from(previous_pk)

                if property:
                    controlinformation.copy_property_from(previous_pk)

                if debits:
                    controlinformation.copy_debits_from(previous_pk)

                controlinformation.closed_address = True
                controlinformation.closed_teaching_1st_semestry = True
                controlinformation.closed_teaching_2nd_semestry = True
                controlinformation.closed_property = True
                controlinformation.closed_debits = True
                controlinformation.closed_health = True
                controlinformation.save(saving=True)
            else:
                controlinformation = ControlInformation()
                controlinformation.employee = employee
                controlinformation.year = newyear
                controlinformation.open_date_teaching_1st_semestry = datetime(
                    int(newyear), 3, 1
                )
                controlinformation.close_date_teaching_1st_semestry = datetime(
                    int(newyear), 3, 31
                )
                controlinformation.open_date_teaching_2nd_semestry = datetime(
                    int(newyear), 8, 1
                )
                controlinformation.close_date_teaching_2nd_semestry = datetime(
                    int(newyear), 8, 31
                )
                controlinformation.open_date_address = datetime(int(newyear), 2, 1)
                controlinformation.close_date_address = datetime(int(newyear), 2, 28)
                controlinformation.open_date_property = datetime(int(newyear), 5, 1)
                controlinformation.close_date_property = datetime(int(newyear), 5, 31)
                controlinformation.open_date_debits = datetime(int(newyear), 5, 1)
                controlinformation.close_date_debits = datetime(int(newyear), 5, 31)
                controlinformation.open_date_health = datetime(int(newyear), 1, 1)
                controlinformation.close_date_health = datetime(int(newyear), 1, 31)
                controlinformation.closed_address = True
                controlinformation.closed_teaching_1st_semestry = True
                controlinformation.closed_teaching_2nd_semestry = True
                controlinformation.closed_property = True
                controlinformation.closed_debits = True
                controlinformation.closed_health = True
                controlinformation.save(saving=True)
            if task_father:
                task = Task.objects.get(uuid=task_father)
                task.info(
                    "Terminado: MP%s - %s" % (str(membro), employee.pessoa_fisica.nome),
                    pct_progress=Decimal(inc_progress),
                )
    except Exception as err:
        log.exception(str(err))
        has_exception = err
        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info(
                "Erro: MP%s - %s<br/>%s"
                % (str(membro), employee.pessoa_fisica.nome, err),
                pct_progress=Decimal(inc_progress),
            )
    if has_exception:
        raise str(has_exception)


def get_action(action):
    action_unicode = ""
    if action == "2":
        action_unicode = "ABERTURA"
    if action == "3":
        action_unicode = "FECHAMENTO"
    return action_unicode


def get_criteria(criteria):

    keys = {
        1: "VAZIO",
        2: "RESIDÊNCIA",
        3: "DOCÊNCIA (1º SEMESTRE)",
        4: "DOCÊNCIA (2º SEMESTRE)",
        5: "BENS e DIREITOS",
        6: "DÍVIDAS E ÔNUS REAIS",
        7: "SAÚDE",
        8: "DECLARAÇÃO DO IRPF",
    }

    return keys.get(criteria, 1)


@app.task()
def schedule_action(
    task, hook, action_type, action_date, criteria, year, employee, user, apply_to=None
):
    state = "failed"
    message = "<b>SRDIR</b>: Erro ao adicionar novo ano"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        initial_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        set_current_user(user)
        message = (
            "<b>SRDIR</b>: Realizando agendamento...<br /><ul><li>%s | %s | %s</li></ul>"
            % (
                ("<b>" + str(year) + "</b>"),
                ("<b>" + get_action(action_type) + "</b>"),
                ("<b>" + get_criteria(int(criteria)) + "</b>"),
            )
        )
        task.message = message
        task.state = "ready"
        task.save()
        task.info(msg="Iniciando...", pct_progress=0.001)
        srdirs = ControlInformation.objects.filter(year=year)

        if apply_to:
            srdirs = srdirs.filter(employee__tipo=apply_to)

        if employee:
            srdirs = srdirs.filter(employee=employee)
        inc_progress = 100.0 / srdirs.count()
        rst = False
        fail = False
        result = None
        job = group(
            [
                schedule_action_employee.s(
                    srdir.pk,
                    action_type,
                    action_date,
                    criteria,
                    user,
                    task_father=task.uuid,
                    inc_progress=inc_progress,
                )
                for srdir in srdirs
            ]
        )
        result = job.apply_async()
        while not (rst):
            rst = result.ready() if result else True
            time.sleep(1)
        fail = result.failed() if result else False
        if not (fail):
            state = "ready"
            final_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            message = (
                "<b>SRDIR</b>: Agendamento concluída com sucesso!<br /><ul><li>%s</li></ul>"
                % (("Ano: <b>" + str(year) + "</b>"))
            )
        else:
            state = "failed"
            message = "<b>SRDIR</b>: Erro ao agendar ação"
        task.finish_execution(msg=message)
    except Exception as err:
        log.exception(str(err))
        has_exception = err
        state = "failed"
        message = "<b>SRDIR</b>: Erro ao agendar ação"
        task.finish_execution(msg=message, status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def schedule_action_employee(
    srdir_pk, action_type, action_date, criteria, user, task_father=None, inc_progress=0
):
    has_exception = None
    try:
        set_current_user(user)
        srdir = ControlInformation.objects.get(pk=srdir_pk)
        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info(
                "Iniciando: MP%s - %s"
                % (srdir.employee.matricula, srdir.employee.pessoa_fisica.nome)
            )
        action_date = (
            datetime.strptime(action_date, "%d/%m/%Y") if action_date != "" else None
        )
        if action_type == "2":
            close_date = action_date + timedelta(days=10)
            if criteria == "2":
                srdir.open_date_address = action_date
                srdir.close_date_address = close_date
            if criteria == "3":
                srdir.open_date_teaching_1st_semestry = action_date
                srdir.close_date_teaching_1st_semestry = close_date
            if criteria == "4":
                srdir.open_date_teaching_2nd_semestry = action_date
                srdir.close_date_teaching_2nd_semestry = close_date
            if criteria == "5":
                srdir.open_date_property = action_date
                srdir.close_date_property = close_date
            if criteria == "6":
                srdir.open_date_debits = action_date
                srdir.close_date_debits = close_date
            if criteria == "7":
                srdir.open_date_health = action_date
                srdir.close_date_health = close_date
            if criteria == "8":
                srdir.open_date_irpf = action_date
                srdir.close_date_irpf = close_date
        if action_type == "3":
            if criteria == "2":
                srdir.close_date_address = action_date
            if criteria == "3":
                srdir.close_date_teaching_1st_semestry = action_date
            if criteria == "4":
                srdir.close_date_teaching_2nd_semestry = action_date
            if criteria == "5":
                srdir.close_date_property = action_date
            if criteria == "6":
                srdir.close_date_debits = action_date
            if criteria == "7":
                srdir.close_date_health = action_date
            if criteria == "8":
                srdir.close_date_irpf = action_date
        srdir.save(saving=True)
        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info(
                "Terminado: MP%s - %s"
                % (srdir.employee.matricula, srdir.employee.pessoa_fisica.nome),
                pct_progress=Decimal(inc_progress),
            )
    except Exception as err:
        log.exception(str(err))
        has_exception = err
        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info(
                "Erro: MP%s - %s<br/>%s"
                % (srdir.employee.matricula, srdir.employee.pessoa_fisica.nome),
                pct_progress=Decimal(inc_progress),
            )
    if has_exception:
        raise has_exception
