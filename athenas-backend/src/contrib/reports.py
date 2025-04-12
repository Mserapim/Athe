# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from functools import partial
import json
import os
import time

from celery import Celery
from django.conf import settings
from django.utils import timezone

from contrib.jasper import Client
from contrib.utils import getLogger
from default.websocket import RemoteEmmiter
from engine.mq.models import Task


log = getLogger("tasker")

app = Celery("report")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task
def start_report(report, report_name, params, hook, task, success, output_format="PDF"):
    client = Client.from_config(getattr(settings, "JASPER_CONFIG", {}))
    cache_path = getattr(settings, "CACHE", {}).get("jreport", None)

    try:
        log.info("Iniciando a geração de relatório.")
        with client.auth() as session:
            log.info("Autenticado com sucesso no gerador de relatório.")
            log.info("Solicitando o relatório.")

            qid = session.report_executation(
                report, params, output_format=output_format
            )
            ready = False
            task_fields = {}

            while not ready:
                status = session.report_executation_status(qid)
                ready = status.get("value") not in ("execution", "queued")

                if status.get("value") == "ready":
                    detail = session.report_executation_detail_exports(qid)
                    outid = detail.get("id")

                    resp = session.report_executation_output(qid, outid)
                    filename = os.path.join(cache_path, "-".join([qid, outid]))

                    with open(filename, "wb") as fd:
                        for data in iter(partial(resp.read, 8192), b""):
                            fd.write(data)

                    msg_params = locals()
                    msg_params.update(
                        deadline=(datetime.now() + timedelta(days=2)).strftime(
                            "%d/%m/%Y %H:%M"
                        )
                    )

                    task_fields.update(
                        {
                            "state": "ready",
                            "data": json.dumps({"queue": qid, "outid": outid}),
                            "message": success % msg_params,
                        }
                    )

                    # Emite mensagem (websocket) para download automático
                    try:
                        if not params.get("origem_apiv2", False):
                            task_obj = Task.objects.get(uuid=task)
                            default_filename = f'relatorio-{timezone.now().strftime("%Y-%m-%d-%H-%M-%S")}'
                            RemoteEmmiter.emmit_for_user(
                                task_obj.owner,
                                "report-ready",
                                path=f'/athenas/MQReportBuilder/file/?uuid={msg_params["task"]}&output_format={msg_params["output_format"]}',
                                filename=f"{params.get('outfile', default_filename)}.{output_format.lower()}",
                            )
                    except Exception as e:
                        log.exception(e)

                    log.info("Relatório gerado com sucesso.")
                elif status.get("value") == "failed":
                    raise Exception(
                        status.get("errorDescriptor", {}).get("message", "desconhecido")
                    )
                else:
                    task_fields.update(state=status.get("value"))

                Task.objects.filter(uuid=task).update(**task_fields)
                time.sleep(0.5)
    except Exception as e:
        log.exception(e)
        Task.objects.filter(uuid=task).update(state="failed", message=str(e))
        raise e
