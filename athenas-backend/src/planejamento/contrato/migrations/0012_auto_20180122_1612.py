# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0011_auto_20170623_0937"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contrato",
            name="numero",
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name="contrato",
            name="numero_processo",
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name="contrato",
            name="numero_processo_mae",
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
    ]
