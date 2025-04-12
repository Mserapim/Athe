# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0032_auto_20161123_1526"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="gestorprogressoes",
            name="posse_servidor",
        ),
        migrations.RemoveField(
            model_name="gestorprogressoes",
            name="progressao_atual",
        ),
        migrations.RemoveField(
            model_name="gestorprogressoes",
            name="ref_atual",
        ),
        migrations.RemoveField(
            model_name="gestorprogressoes",
            name="ref_progressao",
        ),
        migrations.AddField(
            model_name="contracheque",
            name="changes",
            field=models.PositiveIntegerField(default=0, blank=True),
        ),
        migrations.DeleteModel(
            name="GestorProgressoes",
        ),
    ]
