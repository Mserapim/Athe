# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0030_digital_sign"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordinacereformulated",
            name="extract_of_port",
            field=models.TextField(null=True, blank=True),
        ),
    ]
