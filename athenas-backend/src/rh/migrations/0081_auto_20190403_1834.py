# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models
from rh.models import Lotacao


def up(apps, schema_editor):
    print("Marcando flag que habilita procedimentos extrajudiciais")
    Lotacao.objects.exclude(executionorgan=None).update(allow_lawsuit=True)


def down(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0080_auto_20190401_2020"),
    ]

    operations = [
        migrations.AddField(
            model_name="lotacao",
            name="allow_lawsuit",
            field=models.BooleanField(
                default=False, verbose_name="Habilita Procedimentos Extrajudiciais"
            ),
        ),
        migrations.RunPython(up, down),
    ]
