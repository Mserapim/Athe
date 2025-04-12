# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0010_auto_20151217_1053"),
    ]

    operations = [
        migrations.AddField(
            model_name="pessoa",
            name="kind",
            field=models.CharField(max_length=32, verbose_name="Tipo", blank=True),
            preserve_default=True,
        ),
    ]
