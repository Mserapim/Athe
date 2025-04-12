# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("siatu", "0004_auto_20151120_1544"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chamado",
            name="base_conhecimento",
            field=models.ManyToManyField(
                related_name="chamados",
                through="siatu.ItemBaseConhecimento",
                to="siatu.BaseConhecimento",
            ),
        ),
        migrations.AlterField(
            model_name="solicitacao",
            name="chamado_anterior",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="siatu.Chamado",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
