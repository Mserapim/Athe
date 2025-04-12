# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("patrimonio", "0009_auto_20180123_1410"),
    ]

    operations = [
        migrations.AddField(
            model_name="notabaixa",
            name="subtype",
            field=models.SmallIntegerField(
                null=True, verbose_name="Subtipo", blank=True, default=1000
            ),
        )
    ]
