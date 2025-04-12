# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apd", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="periodicevaluationperformance",
            name="days_suspended",
            field=models.IntegerField(default=0, null=True),
        ),
    ]
