# -*- coding: utf-8 -*-
import os
from functools import partial
from subprocess import PIPE, Popen

from celery import Celery

from common.saci.models import Attachment
from contrib.utils import getLogger

log = getLogger("tasker")

app = Celery("report")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task()
def process_attached_document(pk):
    attached = Attachment.objects.get(pk=pk)
    attached.process_renderer_pages()


@app.task()
def process_renderer_pages_of_protable_document_executor(
    filebase, dest, start_page, end_page
):
    cmd = [
        '"/usr/bin/convert"',
        "-background",
        "white",
        "-alpha",
        "remove",
        "-limit",
        "memory",
        "256MB",
        "-limit",
        "map",
        "512MB",
        '"-density"',
        '"120"',
        '"-quality"',
        '"0.75"',
        '"%s[%d-%d]"' % (filebase, start_page, end_page - 1),
        '"-resize"',
        '"794"',
        '"%s"' % dest,
    ]

    log.info(" ".join(cmd))
    pid_fd = Popen(" ".join(cmd), shell=True, stdout=PIPE, stderr=PIPE)
    pid_fd.wait()

    log.info("Return code %d", pid_fd.returncode)
    if pid_fd.returncode != 0:
        log.error("Erro processado o arquivo %s", filebase)
