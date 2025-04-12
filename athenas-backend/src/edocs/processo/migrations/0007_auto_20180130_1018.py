# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("processo", "0006_auto_20171221_1431"),
    ]

    operations = [
        migrations.AlterField(
            model_name="processo",
            name="ano",
            field=models.PositiveSmallIntegerField(default=1, verbose_name="Ano"),
        ),
    ]
