# -*- coding: utf-8 -*-
from datetime import datetime
from celery import Celery
from contrib.decorator import validate
from engine.mq.models import Task
from contrib.middleware import set_current_user, get_current_user
from django.template import loader
from contrib.utils import getLogger
from rh.queryregistration.const import OPTIONS_REPORT
from rh.queryregistration.report import (
    get_filename,
    create_gedfile,
    remote_emmiter,
    create_file_xls,
    get_data_report,
    get_data_report_xls,
    set_params_sql,
    get_data_report_xls_full,
)
from rh.cadastralquality.models import RegistrationQuery
from rh.queryregistration.models import Consultation
import pdfkit, os
import base64


log = getLogger(__name__)


app = Celery("queryregistration")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task()
def report_pdf(
    task,
    hook,
    success,
    user,
    title=None,
    params=None,
    tags=None,
    instance=None,
    pk=None,
    html_path=None,
    download=False,
    filename=None,
    mimetype=None,
    extension=None,
    identifier=None,
    save_log=True,
    name_observer=None,
):
    """
    Está Task é responsável por renderizar um template html criar arquivo pdf para o
    relatório de consultas
    Args:
    :params: São os parâmetros passados para o relatório.
    :sql: sql da consulta.
    :tags: Dict com as chaves das tags sql.
    :title: titulo do relatório
    :pk: id da consulta

    """
    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    message = "'<p>Gerando Relatório...</p>'"
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"

        query = eval(instance).objects.get(pk=pk)
        params, sql = set_params_sql(params, tags, query.sql)
        values = get_data_report(sql, params, pk, title, save_log)
        file = get_filename(filename, identifier)
        file_path = file.absolute_path if file else False
        html = loader.render_to_string(html_path, values)
        output = pdfkit.from_string(html, output_path=file_path, options=OPTIONS_REPORT)
        if not file:
            file = create_gedfile(filename, output, mimetype, identifier)
        task.data = {
            "file": file.absolute_path,
            "filename": title,
            "mimetype": mimetype,
            "extension": extension,
        }

        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar criar o relatório."

    task.message = message
    task.state = state
    remote_emmiter(download, task, name_observer)
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def report_xls(
    task,
    hook,
    success,
    user,
    title=None,
    params=None,
    tags=None,
    instance=None,
    pk=None,
    download=False,
    filename=None,
    mimetype=None,
    extension=None,
    identifier=None,
    save_log=True,
):
    """
    Está Task é responsável por renderizar um template html criar arquivo xls para o
    relatório de consultas
    Args:
    :params: São os parâmetros passados para o relatório.
    :sql: sql da consulta.
    :tags: Dict com as chaves das tags sql.
    :title: titulo do relatório
    :pk: id da consulta

    """
    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    message = "'<p>Gerando Relatório...</p>'"
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"

        query = eval(instance).objects.get(pk=pk)
        params, sql = set_params_sql(params, tags, query.sql)
        values = get_data_report(sql, params, pk, title, save_log)
        file = get_filename(filename, identifier)
        file_path = file.absolute_path if file else False
        output = create_file_xls([values], file_path)
        if not file:
            file = create_gedfile(filename, output, mimetype, identifier)
        task.data = {
            "file": file.absolute_path,
            "filename": title,
            "mimetype": mimetype,
            "extension": extension,
        }
        remote_emmiter(download, task)

        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar criar o relatório."

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def report_xls_full(
    task,
    hook,
    success,
    user,
    title=None,
    params=None,
    instance=None,
    download=False,
    filename=None,
    mimetype=None,
    extension=None,
    identifier=None,
    save_log=False,
):
    """
    Está Task é responsável por renderizar um template html criar arquivo xls para o
    relatório de consultas
    Args:
    :params: São os parâmetros passados para o relatório.
    :sql: sql da consulta.
    :tags: Dict com as chaves das tags sql.
    :title: titulo do relatório
    :pk: id da consulta

    """
    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    message = "'<p>Gerando Relatório...</p>'"
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"

        query = list(eval(instance).objects.filter().values("pk", "sql", "title"))
        values = get_data_report_xls_full(query, params, save_log)

        file = get_filename(filename, identifier)
        file_path = file.absolute_path if file else False
        output = create_file_xls([values], file_path)
        if not file:
            file = create_gedfile(filename, output, mimetype, identifier)
        task.data = {
            "file": file.absolute_path,
            "filename": title,
            "mimetype": mimetype,
            "extension": extension,
        }
        remote_emmiter(download, task)

        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar criar o relatório."

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception
