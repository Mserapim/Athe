# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dirf", "0007_auto_20160217_1802"),
    ]

    operations = [
        migrations.AddField(
            model_name="declaracao",
            name="rectified_receipt",
            field=models.CharField(
                default=b"", max_length=12, verbose_name=b"Recibo retificado"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="demonstrativo",
            name="version",
            field=models.PositiveSmallIntegerField(
                default=1, verbose_name=b"Vers\xc3\xa3o"
            ),
            preserve_default=True,
        ),
    ]
