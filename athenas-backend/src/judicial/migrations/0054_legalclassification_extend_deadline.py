# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0053_generalmotion_install"),
    ]

    operations = [
        migrations.AddField(
            model_name="legalclassification",
            name="extend_deadline",
            field=models.BooleanField(default=False),
        ),
    ]
