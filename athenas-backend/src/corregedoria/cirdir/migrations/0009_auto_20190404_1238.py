# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cirdir", "0008_auto_20190322_1939"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="evaluator",
            name="created_by",
        ),
        migrations.RemoveField(
            model_name="evaluator",
            name="modified_by",
        ),
        migrations.AlterField(
            model_name="health",
            name="evaluator",
            field=models.ForeignKey(
                related_name="healths",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.DeleteModel(
            name="Evaluator",
        ),
    ]
