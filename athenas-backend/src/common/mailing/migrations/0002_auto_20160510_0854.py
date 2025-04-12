# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mailing", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="code",
            field=models.CharField(db_index=True, max_length=10, blank=True),
        ),
        migrations.AlterField(
            model_name="address",
            name="locality",
            field=models.CharField(max_length=150, blank=True),
        ),
        migrations.AlterField(
            model_name="address",
            name="neighborhood",
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name="common",
            name="name",
            field=models.CharField(max_length=150, blank=True),
        ),
    ]
