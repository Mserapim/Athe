# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0062_deadlinelog"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pouch",
            name="from_location",
            field=models.ForeignKey(
                related_name="+", to="rh.Lotacao", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
