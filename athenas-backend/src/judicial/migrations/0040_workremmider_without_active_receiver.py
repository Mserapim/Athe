# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys

from django.db import migrations, models


def up(apps, schema_editor):
    Empleryee = apps.get_model("rh.Servidor")
    WorkerReminder = apps.get_model("judicial.WorkerReminder")

    print(" ", end="")
    for wrm in WorkerReminder.objects.filter(receiver__ativo=False):
        WorkerReminder.objects.filter(pk=wrm.pk).update(
            receiver=Empleryee.objects.filter(ativo=True).get(
                pessoa_fisica_id=wrm.receiver.pessoa_fisica_id
            )
        )
        print("\033[1m\033[32m+\033[0m", end="")
        sys.stdout.flush()


def down(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0039_populate_last_part_lawsuit"),
    ]

    operations = [migrations.RunPython(up, down)]
