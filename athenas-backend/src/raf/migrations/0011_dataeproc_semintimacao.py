# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0010_auto_20170927_1557"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataeproc",
            name="semintimacao",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
