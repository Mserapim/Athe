# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0013_auto_20160728_1353"),
    ]

    operations = [
        migrations.AddField(
            model_name="movimentacao",
            name="physical",
            field=models.BooleanField(default=False),
        ),
    ]
