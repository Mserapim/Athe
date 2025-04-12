# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0027_auto_20160725_1611"),
    ]

    operations = [
        migrations.AddField(
            model_name="pessoafisica",
            name="renda_familiar",
            field=models.DecimalField(
                null=True,
                verbose_name="Renda Familiar",
                max_digits=6,
                decimal_places=2,
                blank=True,
            ),
        ),
    ]
