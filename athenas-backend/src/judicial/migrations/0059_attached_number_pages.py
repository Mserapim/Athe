# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0058_lawsuit_matter"),
    ]

    operations = [
        migrations.AddField(
            model_name="attached",
            name="number_pages",
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
    ]
