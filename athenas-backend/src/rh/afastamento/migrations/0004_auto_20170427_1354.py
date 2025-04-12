# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0043_auto_20170427_1353"),
        ("afastamento", "0003_auto_20160818_0946"),
    ]

    operations = [
        migrations.CreateModel(
            name="AfastamentoDisponibilidade",
            fields=[
                (
                    "afastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.Afastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "posse",
                    models.ForeignKey(
                        related_name="disponibilidade",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.MovimentacaoPosse",
                    ),
                ),
            ],
            options={
                "db_table": "afastamento_disponibilidade",
                "verbose_name": "Afastamento Disponibilidade",
            },
            bases=("afastamento.afastamento",),
        ),
        migrations.AddField(
            model_name="licencasaude",
            name="acidente_transito",
            field=models.IntegerField(default=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="baselicencaafastamento",
            name="designation_exercise",
            field=models.ManyToManyField(
                related_name="departures_exercise", to="rh.ServidorLotacao"
            ),
        ),
        migrations.AlterField(
            model_name="baselicencaafastamento",
            name="prorrogacao",
            field=models.ManyToManyField(
                related_name="afastamento",
                verbose_name="Prorroga\xe7\xe3o",
                to="rh.Prorrogacao",
            ),
        ),
    ]
