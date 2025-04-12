# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0036_auto_20161206_1623"),
    ]

    operations = [
        migrations.AddField(
            model_name="cargo",
            name="remunerated",
            field=models.BooleanField(default=True, verbose_name="Remunerado"),
        ),
    ]
