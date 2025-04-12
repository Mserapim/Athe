# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0010_auto_20181226_1915"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="type_of",
            field=models.PositiveIntegerField(
                default=3, null=True, verbose_name="Tipo", blank=True
            ),
        ),
    ]
