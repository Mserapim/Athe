# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0039_auto_20170410_1558"),
    ]

    operations = [
        migrations.AddField(
            model_name="extrapaymentperiod",
            name="close_prev_period",
            field=models.BooleanField(default=False),
        )
    ]
