# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0007_auto_20151113_1022"),
    ]

    operations = [
        migrations.CreateModel(
            name="Lawyer",
            fields=[
                (
                    "pessoafisica_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.PessoaFisica",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "oab",
                    models.CharField(max_length=20, verbose_name="OAB", blank=True),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("rh.pessoafisica",),
        ),
        migrations.AlterModelOptions(
            name="servidorlotacao",
            options={
                "ordering": ["-data_vigencia_inicio"],
                "verbose_name": "Lota\xe7\xe3o do servidor",
            },
        ),
        migrations.AlterField(
            model_name="declaracaoatividade",
            name="data_encerramento",
            field=models.DateField(null=True, verbose_name="Encerramento", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="declaracaoatividade",
            name="lotacao",
            field=models.ForeignKey(
                verbose_name="Local de trabalho",
                blank=True,
                to="rh.Lotacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
