# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0007_auto_20170914_0813"),
    ]

    operations = [
        migrations.AddField(
            model_name="subitemcalculate",
            name="previous_month",
            field=models.BooleanField(default=False),
        ),
    ]
