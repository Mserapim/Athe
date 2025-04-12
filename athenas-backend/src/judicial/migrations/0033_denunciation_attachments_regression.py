# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys

from django.db import migrations, models
from judicial.models import Denunciation, AssessmentNoticeOffice, Attached


def up_fn(*args, **kwargs):
    print(" ", end="")

    for den in Denunciation.objects.filter(lawsuit__origin__attachments__isnull=False):
        for attachement in den.lawsuit.origin.attachments.filter():
            if not Attached.objects.filter(file_descriptor=attachement.attach).exists():
                obj = Attached(
                    attached_document=den,
                    title=attachement.title,
                    file_descriptor=attachement.attach,
                )
                try:
                    obj.skip_read_only_validate = True
                    obj.save()
                    print("+", end="")
                except Exception as e:
                    print("!(%s)" % e, end="")

        if not den.legal_signs.exists():
            Denunciation.objects.filter(pk=den.pk).update(cache_rendered=None)
            Denunciation.objects.filter(pk=den.pk).update(
                cache_rendered=Denunciation.objects.get(pk=den.pk).rendered
            )

        sys.stdout.flush()


def down_fn(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0032_auto_20170609_1704"),
    ]

    operations = [migrations.RunPython(up_fn, down_fn)]
