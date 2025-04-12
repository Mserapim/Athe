# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0011_dataeproc_semintimacao"),
    ]

    operations = [
        migrations.AddField(
            model_name="subitem",
            name="typesubitem",
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name="Tipo", blank=True
            ),
        ),
    ]
