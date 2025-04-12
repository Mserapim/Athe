# -*- coding: utf-8 -*-
from django.db import migrations
from django.conf import settings
from django.core.management import call_command

import os
import datetime

from rh.gfp.models import Folha


def up(apps, schema_editor):
    print("Running forward...")

    julho = datetime.date(2023, 7, 1)
    Folha.objects.filter(available_pvf=False, dt_fechamento__lt=julho).update(
        available_pvf=True
    )
    print("Atualizando folhas antigas")


def down(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [("gfp", "0118_auto_20230829_2307")]

    operations = [
        migrations.RunPython(up, down),
    ]
