# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0008_subitemcalculate_previous_month"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataeproc",
            name="instancia",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
