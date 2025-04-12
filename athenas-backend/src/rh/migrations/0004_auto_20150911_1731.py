# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0003_auto_20150828_1417"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnonymousPerson",
            fields=[
                (
                    "pessoa_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.Pessoa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=("rh.pessoa",),
        ),
        migrations.AlterModelOptions(
            name="movimentacaosubstituicao",
            options={
                "ordering": ["data_inicio"],
                "verbose_name": "Movimenta\xe7\xe3o de Substitui\xe7\xe3o",
            },
        ),
    ]
