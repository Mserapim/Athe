# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0003_auto_20161028_1055"),
    ]

    operations = [
        migrations.AddField(
            model_name="choice",
            name="description",
            field=models.CharField(default="", max_length=400, blank=True),
        ),
    ]
