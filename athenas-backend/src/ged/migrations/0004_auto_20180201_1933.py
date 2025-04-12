# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ged", "0003_auto_20151014_1609"),
    ]

    operations = [
        migrations.AlterField(
            model_name="arquivo",
            name="file",
            field=models.CharField(unique=True, max_length=32),
        ),
        migrations.AlterUniqueTogether(
            name="arquivo",
            unique_together=set([]),
        ),
    ]
