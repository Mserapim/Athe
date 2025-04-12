# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0004_auto_20180612_1700"),
    ]

    operations = [
        migrations.AddField(
            model_name="inspection",
            name="finalized",
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name="inspection",
            name="finalized_at",
            field=models.DateField(null=True, blank=True),
        ),
    ]
