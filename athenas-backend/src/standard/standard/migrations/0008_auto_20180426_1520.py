# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0007_auto_20180404_1937"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="choice",
            options={"ordering": ("app_label", "name", "-order_weight", "value")},
        ),
    ]
