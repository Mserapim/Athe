# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0013_notificationhistory"),
    ]

    operations = [
        migrations.AddField(
            model_name="notificationhistory",
            name="deadline",
            field=models.DateField(null=True, blank=True),
        ),
    ]
