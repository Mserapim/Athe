# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usefulday", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="parsenonworkingday",
            name="processed",
            field=models.BooleanField(
                default=False, verbose_name="Registro processado?"
            ),
        ),
        migrations.AlterField(
            model_name="nonworkingday",
            name="abrangency",
            field=models.PositiveSmallIntegerField(
                verbose_name="Abrang\xeancia",
                choices=[(1, "Nacional"), (2, "Estadual"), (3, "Municipal")],
            ),
        ),
        migrations.AlterField(
            model_name="nonworkingday",
            name="document",
            field=models.ForeignKey(
                related_name="nonworkingdays",
                verbose_name="Arquivo",
                blank=True,
                to="ged.Arquivo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="nonworkingday",
            name="is_partial",
            field=models.BooleanField(default=False, verbose_name="Parcial"),
        ),
        migrations.AlterField(
            model_name="nonworkingday",
            name="kind",
            field=models.PositiveSmallIntegerField(
                verbose_name="Tipo",
                choices=[(1, "Feriado"), (2, "Ponto Facultativo"), (3, "Suspens\xe3o")],
            ),
        ),
        migrations.AlterField(
            model_name="parsenonworkingday",
            name="nonworkingday",
            field=models.ForeignKey(
                related_name="parsenonworkingdays",
                verbose_name="Dia n\xe3o \xfatil",
                to="usefulday.NonWorkingDay",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="parsenonworkingday",
            name="place",
            field=models.ForeignKey(
                related_name="parsenonworkingdays",
                verbose_name="Cidade",
                blank=True,
                to="rh.Localidade",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
