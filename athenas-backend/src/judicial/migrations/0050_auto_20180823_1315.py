# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0049_auto_20180814_1804"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attached",
            name="title",
            field=models.CharField(max_length=250, blank=True),
        ),
    ]
