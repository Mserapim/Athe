# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        # ('rh', '0079_auto_20190204_1239'),
        ("inspection", "0022_auto_20190126_1556"),
    ]

    operations = [
        migrations.AddField(
            model_name="inspection",
            name="inspector_prosecutors",
            field=models.ManyToManyField(
                related_name="inspector_prosecutors", to="rh.Servidor"
            ),
        ),
    ]
