# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0005_auto_20170406_1512"),
    ]

    operations = [
        migrations.AlterField(
            model_name="configuration",
            name="itens",
            field=models.ManyToManyField(
                related_name="configuration", to="standard.Item"
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="type",
            field=models.PositiveIntegerField(
                default=0, null=True, verbose_name="Tipo", blank=True
            ),
        ),
    ]
