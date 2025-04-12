# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0002_auto_20160510_0854"),
    ]

    operations = [
        migrations.AlterField(
            model_name="choice",
            name="cache_path",
            field=models.CharField(db_index=True, max_length=120, blank=True),
        ),
    ]
