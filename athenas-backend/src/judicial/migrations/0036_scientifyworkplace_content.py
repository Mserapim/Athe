# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0035_auto_20170725_1043"),
    ]

    operations = [
        migrations.AddField(
            model_name="scientifyworkplace",
            name="content",
            field=models.TextField(null=True, blank=True),
        ),
    ]
