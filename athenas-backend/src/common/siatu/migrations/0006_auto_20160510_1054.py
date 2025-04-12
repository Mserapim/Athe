# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("siatu", "0005_auto_20160510_0854"),
    ]

    operations = [
        migrations.AlterField(
            model_name="status",
            name="motivo",
            field=models.CharField(max_length=300, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="status",
            name="previsao_fim",
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="status",
            name="terceirizada",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="siatu.Terceirizada",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
