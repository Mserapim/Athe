# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0018_auto_20160428_1043"),
    ]

    operations = [
        migrations.AddField(
            model_name="cargoquadro",
            name="military",
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
