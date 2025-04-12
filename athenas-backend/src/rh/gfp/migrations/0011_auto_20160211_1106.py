# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0010_auto_20160203_1635"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rraemployee",
            name="factor",
            field=models.DecimalField(
                default=0, verbose_name="Fator", max_digits=8, decimal_places=4
            ),
            preserve_default=True,
        ),
    ]
