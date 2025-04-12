# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0004_auto_20170818_1503"),
    ]

    operations = [
        migrations.AddField(
            model_name="activityadjustment",
            name="initial_message",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="activityadjustment",
            name="activity",
            field=models.ForeignKey(
                related_name="adjustment", to="raf.Activity", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
