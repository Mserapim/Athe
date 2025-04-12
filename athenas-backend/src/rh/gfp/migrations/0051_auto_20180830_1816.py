# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0050_auto_20180509_1752"),
    ]

    operations = [
        migrations.AddField(
            model_name="paycheckdifference",
            name="employer_contribution_to_pay",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Valor/Empregador a Pagar", blank=True
            ),
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="value_to_pay",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Valor a Pagar", blank=True
            ),
        ),
    ]
