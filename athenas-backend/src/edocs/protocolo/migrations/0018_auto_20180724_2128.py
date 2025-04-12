# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0017_auto_20180115_1048"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attachment",
            name="title",
            field=models.CharField(max_length=260),
        ),
    ]
