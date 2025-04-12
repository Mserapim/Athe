# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0051_auto_20180830_1816"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paycheckdifference",
            name="employer_contribution_to_pay",
            field=models.DecimalField(
                default=0,
                verbose_name="Valor/Empregador a Pagar",
                max_digits=19,
                decimal_places=2,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="paycheckdifference",
            name="value_to_pay",
            field=models.DecimalField(
                default=0,
                verbose_name="Valor a Pagar",
                max_digits=19,
                decimal_places=2,
                blank=True,
            ),
        ),
    ]
