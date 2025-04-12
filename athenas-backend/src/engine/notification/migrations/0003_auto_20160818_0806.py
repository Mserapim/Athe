# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notification", "0002_auto_20160229_1715"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="params",
            field=models.TextField(verbose_name="Params"),
        ),
    ]
