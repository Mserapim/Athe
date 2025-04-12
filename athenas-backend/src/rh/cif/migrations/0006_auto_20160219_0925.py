# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cif", "0005_referenceperiod_main_period"),
    ]

    operations = [
        migrations.AddField(
            model_name="controlinformationmember",
            name="lock_address",
            field=models.BooleanField(
                default=False, verbose_name="Bloqueio para Endere\xe7o"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="controlinformationmember",
            name="lock_debts",
            field=models.BooleanField(
                default=False, verbose_name="Bloqueio para D\xedvidas"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="controlinformationmember",
            name="lock_property",
            field=models.BooleanField(default=False, verbose_name="Bloqueio para Bens"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="controlinformationmember",
            name="lock_teaching",
            field=models.BooleanField(
                default=False, verbose_name="Bloqueio para Doc\xeancia"
            ),
            preserve_default=True,
        ),
    ]
