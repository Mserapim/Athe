# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planoconta", "0004_auto_20160510_0854"),
    ]

    operations = [
        migrations.AddField(
            model_name="provisionmanager",
            name="pension_system",
            field=models.PositiveSmallIntegerField(
                default=1,
                verbose_name="Regime previdenci\xe1rio",
                choices=[(1, "RGPS"), (2, "RPPS"), (3, "MILITAR")],
            ),
            preserve_default=False,
        ),
    ]
