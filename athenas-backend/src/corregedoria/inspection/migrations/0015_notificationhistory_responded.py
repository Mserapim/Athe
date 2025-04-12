# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0014_notificationhistory_deadline"),
    ]

    operations = [
        migrations.AddField(
            model_name="notificationhistory",
            name="responded",
            field=models.BooleanField(default=False),
        ),
    ]
