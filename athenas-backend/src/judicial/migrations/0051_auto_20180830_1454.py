# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0066_auto_20180830_1454"),
        ("judicial", "0050_auto_20180823_1315"),
    ]

    operations = [
        migrations.AddField(
            model_name="executionorgan",
            name="attribution_document",
            field=models.ForeignKey(
                related_name="executionorgan_attribution_document",
                verbose_name="Documento de atribui\xe7\xe3o",
                blank=True,
                to="rh.Publicacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="executionorgan",
            name="occupation_area",
            field=models.CharField(
                db_index=True,
                max_length=4000,
                null=True,
                verbose_name="\xc1rea de atua\xe7\xe3o",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="executionorgan",
            name="attribution",
            field=models.CharField(
                db_index=True,
                max_length=4000,
                verbose_name="Atribui\xe7\xe3o",
                blank=True,
            ),
        ),
    ]
