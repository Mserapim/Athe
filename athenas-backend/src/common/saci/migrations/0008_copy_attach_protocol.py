# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from common.saci.models import Attendance, Attachment
from contrib.utils import getLogger

log = getLogger(__name__)


def up_fn(*args, **kwargs):

    query = None

    query = Attendance.objects.filter(protocol__attachments__isnull=False).distinct()

    for attendance in query:
        log.info("***********************************************")
        for attach in attendance.protocol.attachment_list:
            obj = Attachment(
                attendance=attendance,
                title=attach.title,
                file_descriptor=attach.attach,
                observation=attach.observation,
            )

            obj.skip_read_only_validate = True
            log.info("Criando attach para o atendimento %s " % attendance)
            obj.save()


def down_fn(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("saci", "0007_attachment"),
    ]

    operations = [migrations.RunPython(up_fn, down_fn)]
