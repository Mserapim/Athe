# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.db import migrations, models
from django.core.management import call_command


def up(apps, schema_editor):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    filepath = os.path.join(
        BASE_DIR, "judicial", "fixtures", "0024-choices-council-incident.json"
    )
    print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
    call_command("loaddata", filepath)


def down(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("council", "0002_auto_20170424_1156"),
    ]

    operations = [
        migrations.AddField(
            model_name="rapporteurdocument",
            name="reconsideration",
            field=models.OneToOneField(
                related_name="reconsiderated",
                null=True,
                blank=True,
                to="council.RapporteurDocument",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="councillor",
            name="incident_type",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (101, "Conex\xe3o"),
                    (102, "Preven\xe7\xe3o"),
                    (201, "Impedimento"),
                    (202, "Suspei\xe7\xe3o"),
                    (301, "Aus\xeancia Justificada"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="rapporteurdocument",
            name="rapporteur",
            field=models.ForeignKey(
                related_name="document",
                to="council.Rapporteur",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.RunPython(up, down),
    ]
