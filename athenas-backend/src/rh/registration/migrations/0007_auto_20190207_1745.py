# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0006_auto_20181211_1400"),
    ]

    operations = [
        migrations.AddField(
            model_name="forminformation",
            name="phone_outsider",
            field=models.BooleanField(
                default=False, verbose_name="Telefone no exterior"
            ),
        ),
        migrations.AddField(
            model_name="forminformation",
            name="phone_outsider_diff",
            field=models.BooleanField(default=False),
        ),
    ]
