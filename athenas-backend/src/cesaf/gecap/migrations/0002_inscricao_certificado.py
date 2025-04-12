# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gecap", "0001_initial"),
        ("ged", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="inscricao",
            name="certificado",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                blank=True, to="ged.Arquivo", null=True, on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
    ]
