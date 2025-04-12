# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cif", "0009_auto_20160704_1331"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="authorization_reside_outside",
            field=models.BooleanField(
                default=False,
                verbose_name="Autoriza\xe7\xe3o para residir fora da comarca",
            ),
        ),
    ]
