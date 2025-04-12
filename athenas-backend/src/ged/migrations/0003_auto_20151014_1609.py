# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ged", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.AlterField(
            model_name="arquivo",
            name="acesso",
            field=models.PositiveIntegerField(
                default=3,
                choices=[(1, "PRIVADO"), (2, "PRIVADO AO GRUPO"), (3, "P\xdaBLICO")],
            ),
            preserve_default=True,
        ),
    ]
