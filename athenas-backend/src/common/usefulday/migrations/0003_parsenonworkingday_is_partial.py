# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usefulday", "0002_auto_20181120_1837"),
    ]

    operations = [
        migrations.AddField(
            model_name="parsenonworkingday",
            name="is_partial",
            field=models.BooleanField(default=False),
        ),
    ]
