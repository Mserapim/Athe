# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0036_scientifyworkplace_content"),
    ]

    operations = [
        migrations.AddField(
            model_name="legalclassification",
            name="selectable",
            field=models.BooleanField(default=False),
        ),
    ]
