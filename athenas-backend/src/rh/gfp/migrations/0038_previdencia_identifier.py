# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0037_auto_20170405_1845"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="previdencia",
            name="identifier",
        ),
        migrations.AddField(
            model_name="previdencia",
            name="identifier",
            field=models.PositiveSmallIntegerField(
                default=1, verbose_name="Identificador"
            ),
        ),
    ]
