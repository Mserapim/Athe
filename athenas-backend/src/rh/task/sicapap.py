# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime, timedelta
from logging import getLogger

from celery import Celery

from contrib.middleware import set_current_user
from engine.mq.models import Task
from rh.sicap.utils import SicapBuilder, SicapUtil
from rh.gfp.generators.sicap.protocol import SicapGenerator, SicapHelper

log = getLogger("tasker")

# django.setup()

app = Celery("sicapap")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task
def sicap_maker(task, hook, year, months, user, success, paymentfile=None):
    state = "failed"
    buf = SicapHelper._months_to_unicode(months)
    message = "<p>RH - SICAP AP: Gerando arquivos ...</p>"
    task = Task.objects.get(uuid=task)

    print("sicap_task")

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        set_current_user(user)
        message = "<p>RH - SICAP AP: %s-%s - Gerando arquivos ...</p>" % (buf, year)
        task.message = message
        task.state = "progress"
        task.save()

        SicapGenerator(
            year=year,
            months=months,
            feedback=feedback,
            task=task,
            paymentfile=paymentfile,
        ).generate()
        state = "ready"
        msg_params = locals()
        msg_params.update(
            deadline=(datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y %H:%M")
        )
        msg_params.update(uuid=task.uuid)
        msg_params.update(sicapap="%s%s" % (buf, year))
        message = success % msg_params
        task.data = json.dumps(
            {
                "months": buf,
                "year": year,
                "filename": "%s-%s-%s.zip" % (SicapHelper._file_name(), buf, year),
            }
        )

    except Exception as err:
        log.exception(err)
        has_exception = err
        message = (
            "<p>RH - SICAP AP: %s-%s - Falha na criação de arquivos.</p><p>%s</p>"
            % (buf, year, err)
        )

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task
def sicap_generator(task, hook, year, months, user, success):
    state = "failed"
    buf = SicapUtil._months_to_unicode(months)
    message = "<p>RH - SICAP AP: %s-%s - Gerando arquivos ...</p>" % (buf, year)
    task = Task.objects.get(uuid=task)

    print("sicap_generator")

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        set_current_user(user)
        message = "<p>RH - SICAP AP: %s-%s - Gerando arquivos ...</p>" % (buf, year)
        task.message = message
        task.state = "progress"
        task.save()

        SicapBuilder(year=year, months=months, feedback=feedback)

        state = "ready"
        msg_params = locals()
        msg_params.update(
            deadline=(datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y %H:%M")
        )
        msg_params.update(uuid=task.uuid)
        msg_params.update(sicapap="%s%s" % (buf, year))
        message = success % msg_params
        task.data = json.dumps(
            {
                "months": buf,
                "year": year,
                "filename": "%s-%s-%s.zip" % (SicapUtil._file_name(), buf, year),
            }
        )
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = (
            "<p>RH - SICAP AP: %s-%s - Falha na criação de arquivos.</p><p>%s</p>"
            % (buf, year, err)
        )

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception
