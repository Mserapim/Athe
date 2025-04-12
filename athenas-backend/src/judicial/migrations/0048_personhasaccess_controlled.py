# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0047_auto_20180426_1513"),
    ]

    operations = [
        migrations.AddField(
            model_name="personhasaccess",
            name="controlled",
            field=models.BooleanField(default=False),
        ),
    ]
