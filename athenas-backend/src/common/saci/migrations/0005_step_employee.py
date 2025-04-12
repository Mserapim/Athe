# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        # ('rh', '0049_auto_20170629_1632'),
        ("saci", "0004_auto_20161118_1425"),
    ]

    operations = [
        migrations.AddField(
            model_name="step",
            name="employee",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
