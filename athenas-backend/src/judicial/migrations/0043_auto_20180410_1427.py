# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0042_auto_20180409_1522"),
    ]

    operations = [
        migrations.AlterField(
            model_name="executionorgan",
            name="attribution",
            field=models.CharField(db_index=True, max_length=4000, blank=True),
        ),
    ]
