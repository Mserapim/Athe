# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0029_auto_20161114_1147"),
    ]

    operations = [
        migrations.AddField(
            model_name="referencianiveis2d",
            name="estrutura_salarial",
            field=models.ForeignKey(
                related_name="+",
                verbose_name="N\xedvel Salarial",
                blank=True,
                to="gfp.EstruturaTabelaSalarial",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
