# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contabilidade", "0005_auto_20170816_1811"),
    ]

    operations = [
        migrations.AddField(
            model_name="budgetaryindicator",
            name="year",
            field=models.CharField(
                max_length=4, null=True, verbose_name="Ano", blank=True
            ),
        ),
    ]
