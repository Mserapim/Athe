# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profile", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobprofile",
            name="for_activity_statement",
            field=models.BooleanField(
                default=False, verbose_name="Para declara\xe7\xe3o de atividade"
            ),
        ),
    ]
