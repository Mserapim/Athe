# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("compras", "0002_auto_20150810_1114"),
        ("rh", "0001_initial"),
        ("cpl", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.AddField(
            model_name="participante",
            name="pessoa",
            field=models.ForeignKey(
                to="rh.Pessoa", unique=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="licitacao",
            name="processo",
            field=models.ForeignKey(
                related_name="licitacao",
                to="compras.ProcessoAquisicao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
