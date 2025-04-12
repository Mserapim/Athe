# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0001_initial"),
        ("eproc", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="processo",
            name="interessado",
            field=models.ForeignKey(
                to="rh.Servidor", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pagina",
            name="processo",
            field=models.ForeignKey(
                to="eproc.Processo", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
