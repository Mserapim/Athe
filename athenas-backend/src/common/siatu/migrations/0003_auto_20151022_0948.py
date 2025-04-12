# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0006_auto_20150921_1434"),
        ("siatu", "0002_auto_20151015_1018"),
    ]

    operations = [
        migrations.AddField(
            model_name="chamado",
            name="nao_urgente",
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="chamado",
            name="nao_urgente_por",
            field=models.ForeignKey(
                related_name="+", to="rh.Servidor", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
