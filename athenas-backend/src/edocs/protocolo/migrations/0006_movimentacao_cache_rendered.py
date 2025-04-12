# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0005_auto_20150827_1750"),
    ]

    operations = [
        migrations.AddField(
            model_name="movimentacao",
            name="cache_rendered",
            field=models.TextField(null=True),
            preserve_default=True,
        ),
    ]
