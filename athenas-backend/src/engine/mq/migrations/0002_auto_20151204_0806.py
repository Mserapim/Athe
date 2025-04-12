# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("mq", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="progress",
            field=models.DecimalField(null=True, max_digits=6, decimal_places=3),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="task",
            name="progress_message",
            field=models.CharField(max_length=100, null=True),
            preserve_default=True,
        ),
    ]
