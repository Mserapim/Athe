# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0002_auto_20170725_1812"),
    ]

    operations = [
        migrations.AddField(
            model_name="subitem",
            name="blocked",
            field=models.BooleanField(default=False),
        ),
    ]
