# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys

from django.db import migrations, models
import datetime
import django.db.models.deletion
from django.conf import settings


def pp(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


def up(apps, schema_editor):
    Attached = apps.get_model("judicial.Attached")
    PartLawsuit = apps.get_model("judicial.PartLawsuit")
    Manifestation = apps.get_model("judicial.Manifestation")
    Diligence = apps.get_model("judicial.Diligence")
    PartLawsuitAccess = apps.get_model("judicial.PartLawsuitAccess")

    pp(" ", end="")
    for attached in Attached.objects.filter(attached_document__isnull=False):
        try:
            Attached.objects.filter(pk=attached.pk).update(
                created_at=attached.attached_document.created_at,
                created_by=attached.attached_document.created_by,
                modified_at=attached.attached_document.modified_at,
                modified_by=attached.attached_document.modified_by,
            )
        except Exception:
            pp("\033[1m\033[32m-\033[0m", end="")
        else:
            pp("\033[1m\033[33m+\033[0m", end="")

    pp(" ", end="")
    for attached in Attached.objects.filter(
        attached_manifestation__isnull=False,
        attached_manifestation__signed_by__isnull=False,
    ):
        try:
            Attached.objects.filter(pk=attached.pk).update(
                created_at=attached.attached_manifestation.signed_at,
                created_by=attached.attached_manifestation.diligence.signed_by,
                modified_at=attached.attached_manifestation.signed_at,
                modified_by=attached.attached_manifestation.diligence.signed_by,
            )
        except Exception:
            pp("\033[1m\033[32m-\033[0m", end="")
        else:
            pp("\033[1m\033[33m+\033[0m", end="")

    pp(" ", end="")
    for attached in Attached.objects.filter(attached_diligence__isnull=False):
        try:
            Attached.objects.filter(pk=attached.pk).update(
                created_at=attached.attached_diligence.created_at,
                created_by=attached.attached_diligence.created_by,
                modified_at=attached.attached_diligence.modified_at,
                modified_by=attached.attached_diligence.modified_by,
            )
        except Exception:
            pp("\033[1m\033[32m-\033[0m", end="")
        else:
            pp("\033[1m\033[33m+\033[0m", end="")

    pp(" ", end="")
    for attached in Attached.objects.filter(attached_part_access__isnull=False):
        try:
            Attached.objects.filter(pk=attached.pk).update(
                created_at=attached.attached_part_access.created_at,
                created_by=attached.attached_part_access.created_by,
                modified_at=attached.attached_part_access.modified_at,
                modified_by=attached.attached_part_access.modified_by,
            )
        except Exception:
            pp("\033[1m\033[32m-\033[0m", end="")
        else:
            pp("\033[1m\033[33m+\033[0m", end="")


def down(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0028_auto_20170525_0950"),
    ]

    operations = [
        migrations.RunPython(up, down),
    ]
