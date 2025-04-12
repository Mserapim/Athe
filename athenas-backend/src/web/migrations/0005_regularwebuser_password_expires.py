# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0004_auto_20151117_1133"),
    ]

    operations = [
        migrations.AddField(
            model_name="regularwebuser",
            name="password_expires",
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
