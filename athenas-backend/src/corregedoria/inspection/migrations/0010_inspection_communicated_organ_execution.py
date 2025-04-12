# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0009_auto_20180918_1249"),
    ]

    operations = [
        migrations.AddField(
            model_name="inspection",
            name="communicated_organ_execution",
            field=models.BooleanField(default=False),
        ),
    ]
