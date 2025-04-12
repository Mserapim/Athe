# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dirf", "0012_auto_20170216_1007"),
    ]

    operations = [
        migrations.AlterField(
            model_name="demonstrativo",
            name="informacao_complementar",
            field=models.CharField(default=b"", max_length=500),
        ),
        migrations.AlterField(
            model_name="dirfsummary",
            name="info",
            field=models.CharField(
                default=b"", max_length=50, db_index=True, blank=True
            ),
        ),
    ]
