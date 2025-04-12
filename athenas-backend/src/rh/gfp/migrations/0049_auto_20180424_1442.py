# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
from django.core.management import call_command
import os


def up(apps, schema_editor):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    filepath = os.path.join(
        BASE_DIR, "rh", "gfp", "fixtures", "initialdb_0004_natureevents.json"
    )
    print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
    call_command("loaddata", filepath)


def down(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0048_auto_20180327_2010"),
    ]

    operations = [
        migrations.CreateModel(
            name="NatureEvent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        unique=True, max_length=4, verbose_name="N\xfamero"
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="T\xedtulo")),
                (
                    "description",
                    models.CharField(
                        default="",
                        max_length=800,
                        verbose_name="Descri\xe7\xe3o",
                        blank=True,
                    ),
                ),
                ("active", models.BooleanField(default=True, verbose_name="Ativo?")),
            ],
            options={
                "ordering": ("code",),
            },
        ),
        migrations.AddField(
            model_name="evento",
            name="nature_of_event",
            field=models.ForeignKey(
                verbose_name="Natureza (eSocial)",
                blank=True,
                to="gfp.NatureEvent",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.RunPython(up, down),
    ]
