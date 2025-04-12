# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0060_auto_20180227_1602"),
    ]

    operations = [
        migrations.AlterField(
            model_name="docsdadosespecificos",
            name="valor",
            field=models.CharField(default="", max_length=256, verbose_name="Valor"),
        ),
    ]
