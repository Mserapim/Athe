# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0001_initial"),
        ("ouvidoria", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="manifestacao",
            name="protocolo",
            field=models.OneToOneField(
                related_name="manifestacao",
                to="protocolo.Protocolo",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
