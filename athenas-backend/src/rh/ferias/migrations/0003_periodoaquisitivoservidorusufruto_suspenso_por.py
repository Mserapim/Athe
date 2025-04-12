# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0034_auto_20161111_1000"),
        ("ferias", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.AddField(
            model_name="periodoaquisitivoservidorusufruto",
            name="suspenso_por",
            field=models.ForeignKey(
                related_name="ferias_suspensas",
                blank=True,
                to="rh.Servidor",
                help_text="O servidor que suspenendeu essa parcela",
                null=True,
                verbose_name="Suspenso por",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
