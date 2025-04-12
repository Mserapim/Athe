# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0004_choice_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="choice",
            name="label",
            field=models.CharField(max_length=120, verbose_name="Label"),
        ),
    ]
