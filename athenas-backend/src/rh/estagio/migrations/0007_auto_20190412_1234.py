# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("estagio", "0006_auto_20190411_1810"),
    ]

    operations = [
        migrations.AlterField(
            model_name="decisaochefeorgao",
            name="decisao",
            field=models.CharField(
                blank=True,
                max_length=1,
                null=True,
                choices=[(1, "HOMOLOGA"), (2, "N\xc3O HOMOLOGA")],
            ),
        ),
    ]
