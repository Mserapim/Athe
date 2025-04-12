# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0011_auto_20181029_1342"),
    ]

    operations = [
        migrations.AddField(
            model_name="inspection",
            name="communicated_organ_execution_at",
            field=models.DateField(null=True, blank=True),
        ),
    ]
