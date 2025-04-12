# -*- coding: utf-8 -*-
import os
import time
import json
import importlib
from celery import Celery
from contrib.jasper import Client
from django.conf import settings
from engine.mq.models import Task
from contrib.utils import getLogger
from datetime import datetime, timedelta
from functools import partial


log = getLogger("tasker")

app = Celery("corregedoria.reportbuilder.tasks")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task
def generate_file(
    task=None,
    hook=None,
    report=None,
    report_name=None,
    params=None,
    success=None,
    output_format="PDF",
):

    cache_path = getattr(settings, "CACHE", {}).get("jreport", None)

    if success is None:
        success = """<p>O Relatorio <span style="font-weight:bold">%(report_name)s</span> foi gerado com sucesso. Para fazer o download clique no
        <a href="/athenas/MQReportBuilder/file/?uuid=%(task)s&output_format=%(output_format)s">link</a>.
        </p>
        <p>Esta relatório estara disponivel para download até dia <span style="font-weight:bold">%(deadline)s</span></p>"""

    try:
        task_o = Task.objects.get(uuid=task)
        qid = task_o.uuid
        outid = str(hash(datetime.now()))
        ready = False

        filename = os.path.join(cache_path, "-".join([qid, outid]))

        modname, _, clsname = report.rpartition(".")
        mod = importlib.import_module(modname)
        cls = getattr(mod, clsname)

        report_cls = cls(output_file=filename, params=params)
        setattr(report_cls, "current_user", task_o.owner)
        report_cls.build()

        msg_params = locals()

        msg_params.update(
            deadline=(datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y %H:%M")
        )

        task_o.state = "ready"
        task_o.data = json.dumps({"queue": qid, "outid": outid})
        task_o.message = success % msg_params

        task_o.save()
        time.sleep(0.5)
    except Exception as e:
        log.exception(e)
        task_o.state = "failed"
        task_o.message = str(e)
        task_o.save()
        raise e
