# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0063_auto_20180529_2058"),
    ]

    operations = [
        migrations.AddField(
            model_name="pessoa",
            name="email",
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
    ]
