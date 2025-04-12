# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("saci", "0005_step_employee"),
    ]

    operations = [
        migrations.AddField(
            model_name="attendance",
            name="deleted",
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
