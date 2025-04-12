# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        # ('rh', '0080_auto_20190313_1233'),
        ("protocolo", "0018_auto_20180724_2128"),
    ]

    operations = [
        migrations.AddField(
            model_name="groupperson",
            name="locality",
            field=models.ForeignKey(
                related_name="group_person",
                verbose_name="Localidade",
                blank=True,
                to="rh.Localidade",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
