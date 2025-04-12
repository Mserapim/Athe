# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contabilidade", "0004_auto_20160510_0854"),
    ]

    operations = [
        migrations.CreateModel(
            name="BudgetaryIndicator",
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
                ("name", models.CharField(max_length=64, verbose_name="I.O.")),
                (
                    "object_name",
                    models.CharField(max_length=128, verbose_name="Objeto"),
                ),
                (
                    "action",
                    models.ForeignKey(
                        related_name="budgetary_indicators",
                        to="contabilidade.PPAAcao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "source",
                    models.ForeignKey(
                        related_name="budgetary_indicators",
                        to="contabilidade.FonteRecurso",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Indicador Or\xe7ament\xe1rio",
            },
        ),
        migrations.AlterUniqueTogether(
            name="budgetaryindicator",
            unique_together=set([("name", "object_name", "action", "source")]),
        ),
    ]
