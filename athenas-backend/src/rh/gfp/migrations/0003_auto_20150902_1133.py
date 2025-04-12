# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.AlterField(
            model_name="folhatipo",
            name="abreviatura",
            field=models.CharField(
                default="", max_length=20, verbose_name="Abreviatura", blank=True
            ),
            preserve_default=True,
        ),
    ]
