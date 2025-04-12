# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0022_auto_20160817_1618"),
    ]

    operations = [
        migrations.AddField(
            model_name="transparencychoice",
            name="type_event",
            field=models.CharField(
                blank=True,
                max_length=1,
                null=True,
                choices=[("D", "D\xc3\x89BITO"), ("C", "CR\xc3\x89DITO")],
            ),
        ),
        migrations.AlterField(
            model_name="genreevent",
            name="config_transparency",
            field=models.PositiveIntegerField(
                null=True, verbose_name="Portal Transpar\xeancia", blank=True
            ),
        ),
    ]
