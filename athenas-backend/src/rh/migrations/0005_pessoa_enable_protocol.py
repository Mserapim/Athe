# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0004_auto_20150911_1731"),
    ]

    operations = [
        migrations.AddField(
            model_name="pessoa",
            name="enable_protocol",
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
