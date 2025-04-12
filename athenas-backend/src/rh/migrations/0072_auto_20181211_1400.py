# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0071_auto_20181205_2032"),
    ]

    operations = [
        migrations.AddField(
            model_name="endereco",
            name="outsider_citty",
            field=models.CharField(
                max_length=50, null=True, verbose_name="Cidade no Exterior", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="endereco",
            name="municipio",
            field=models.ForeignKey(
                blank=True, to="rh.Localidade", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
