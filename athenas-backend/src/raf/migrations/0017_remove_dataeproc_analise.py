# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0016_dataeproc_analise_tmp"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dataeproc",
            name="analise",
        ),
    ]
