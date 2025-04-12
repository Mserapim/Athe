# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contabilidade", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.AddField(
            model_name="pparevisao",
            name="ativo",
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
