# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0046_remittanceitselforgan"),
    ]

    operations = [
        migrations.AddField(
            model_name="assessmentnoticeoffice",
            name="movement_cache_rendered",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="denunciation",
            name="movement_cache_rendered",
            field=models.TextField(null=True, blank=True),
        ),
    ]
