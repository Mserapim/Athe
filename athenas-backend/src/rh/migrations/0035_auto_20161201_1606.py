# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0034_auto_20161111_1000"),
    ]

    operations = [
        migrations.CreateModel(
            name="Trainee",
            fields=[
                (
                    "servidor_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Estagi\xe1rio",
            },
            bases=("rh.servidor",),
        ),
        migrations.AlterField(
            model_name="dependencia",
            name="tipo",
            field=models.SmallIntegerField(
                default=1,
                choices=[
                    (1, "Imposto de Renda"),
                    (2, "PlanSa\xfade"),
                    (3, "Sal\xe1rio Fam\xedlia"),
                    (4, "Aux\xedlio Creche"),
                    (5, "Previd\xeancia"),
                    (6, "Aux\xedlio Especial"),
                ],
            ),
        ),
    ]
