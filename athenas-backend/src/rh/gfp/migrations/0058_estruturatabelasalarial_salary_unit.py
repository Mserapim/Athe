# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.management import call_command
from django.db import migrations, models


def up(apps, schema_editor):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    filepath = os.path.join(BASE_DIR, "rh", "gfp", "fixtures", "salaryunit.json")
    print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
    call_command("loaddata", filepath)


def down(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0057_auto_20181219_1443"),
    ]

    operations = [
        migrations.RunPython(up, down),
        migrations.AddField(
            model_name="estruturatabelasalarial",
            name="salary_unit",
            field=models.PositiveSmallIntegerField(
                default=5,
                null=True,
                verbose_name="Unidade de sal\xc3\xa1rio fixo",
                choices=[
                    (1, "Por Hora"),
                    (2, "Por Dia"),
                    (3, "Por Semana"),
                    (4, "Por Quinzena"),
                    (5, "Por M\xeas"),
                    (6, "Por Tarefa"),
                    (7, "N\xe3o aplic\xe1vel"),
                ],
            ),
        ),
    ]
