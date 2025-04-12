# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dirf", "0014_auto_20180119_1719"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dialect",
            name="dirf",
        ),
        migrations.RemoveField(
            model_name="dialect",
            name="engine",
        ),
        migrations.AddField(
            model_name="dialect",
            name="last_receipt",
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
    ]
