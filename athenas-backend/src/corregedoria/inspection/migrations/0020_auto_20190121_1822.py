# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0019_auto_20190111_1211"),
    ]

    operations = [
        migrations.AddField(
            model_name="administrativeorganizationarchivedprocedures",
            name="instauration_date",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="existingregisters",
            name="observation",
            field=models.TextField(null=True, blank=True),
        ),
    ]
