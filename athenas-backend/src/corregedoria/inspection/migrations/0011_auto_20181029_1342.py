# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0010_inspection_communicated_organ_execution"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inspection",
            name="finalized",
            field=models.BooleanField(default=False),
        ),
    ]
