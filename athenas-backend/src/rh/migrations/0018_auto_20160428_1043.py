# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0017_auto_20160427_1523"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cargo",
            name="health",
        ),
        migrations.AddField(
            model_name="cargoquadro",
            name="health",
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="cargoquadro",
            name="teacher",
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
