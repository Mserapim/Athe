# -*- coding: utf-8 -*-
import os
import django

from celery import Celery
from logging import getLogger
from ged.models import Arquivo as FileEntry
from ged.views import PDFFileWrapperPyPDF2

log = getLogger("tasker")

app = Celery("ged_sign")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))

# django.setup()


@app.task
def sign_pdf_validation(pk):
    fe = FileEntry.objects.get(pk=pk)

    if not os.path.exists("%s.queue" % fe.absolute_path):
        open("%s.queue" % fe.absolute_path, "x")

    wrapper = PDFFileWrapperPyPDF2(fe)
    wrapper.sign(fe)

    if os.path.exists("%s.queue" % fe.absolute_path):
        os.unlink("%s.queue" % fe.absolute_path)
