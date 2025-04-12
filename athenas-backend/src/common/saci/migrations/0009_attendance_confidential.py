# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("saci", "0008_copy_attach_protocol"),
    ]

    operations = [
        migrations.AddField(
            model_name="attendance",
            name="confidential",
            field=models.BooleanField(default=False),
        ),
    ]
