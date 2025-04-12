# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0021_auto_20180131_1728"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="functionalactivityreport",
            name="process_date",
        ),
        migrations.AddField(
            model_name="dataeproc",
            name="processo_formatado",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
