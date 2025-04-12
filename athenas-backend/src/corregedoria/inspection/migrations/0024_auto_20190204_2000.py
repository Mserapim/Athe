# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0023_inspection_inspector_prosecutors"),
    ]

    operations = [
        migrations.AddField(
            model_name="sign",
            name="employee",
            field=models.ForeignKey(
                related_name="employee_signs",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="inspection",
            name="inspector_prosecutors",
            field=models.ManyToManyField(
                related_name="inspector_prosecutors",
                null=True,
                to="rh.Servidor",
                blank=True,
            ),
        ),
    ]
