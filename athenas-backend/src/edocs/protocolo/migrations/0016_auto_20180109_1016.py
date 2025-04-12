# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0015_auto_20170822_1437"),
    ]

    operations = [
        migrations.AddField(
            model_name="movimentacao",
            name="with_workflow",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="groupgeneralorgan",
            name="department",
            field=models.ForeignKey(
                related_name="group_general_organ",
                verbose_name="Departamento",
                blank=True,
                to="rh.Lotacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="groupperson",
            name="department",
            field=models.ForeignKey(
                related_name="group_person",
                verbose_name="Departamento",
                blank=True,
                to="rh.Lotacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
