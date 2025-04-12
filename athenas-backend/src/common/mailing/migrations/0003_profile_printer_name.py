# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mailing", "0002_auto_20160510_0854"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="printer_name",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
    ]
