# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0006_auto_20170912_0949"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="dataeproc",
            options={
                "ordering": ["membro", "promotoria", "datamovimento"],
                "verbose_name": "DataEproc",
            },
        ),
    ]
