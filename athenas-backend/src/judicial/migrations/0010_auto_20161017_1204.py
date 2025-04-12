# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0009_auto_20161017_0935"),
    ]

    operations = [
        migrations.AlterField(
            model_name="partlawsuit",
            name="page_number",
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name="partlawsuit",
            unique_together=set([("lawsuit", "page_number")]),
        ),
    ]
