# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cif", "0004_auto_20160119_1421"),
    ]

    operations = [
        migrations.AddField(
            model_name="referenceperiod",
            name="main_period",
            field=models.BooleanField(
                default=False, verbose_name="Per\xedodo de refer\xeancia principal"
            ),
            preserve_default=True,
        ),
    ]
