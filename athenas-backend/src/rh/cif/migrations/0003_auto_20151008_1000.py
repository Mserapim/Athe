# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cif", "0002_auto_20151008_0943"),
    ]

    operations = [
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="current_value",
            field=models.DecimalField(
                verbose_name="Situa\xe7\xe3o Atual (R$)",
                max_digits=18,
                decimal_places=2,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="last_value",
            field=models.DecimalField(
                default=0,
                null=True,
                verbose_name="\xdaltima Situa\xe7\xe3o (R$)",
                max_digits=18,
                decimal_places=2,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="property",
            name="current_value",
            field=models.DecimalField(
                verbose_name="Situa\xe7\xe3o Atual (R$)",
                max_digits=18,
                decimal_places=2,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="property",
            name="last_value",
            field=models.DecimalField(
                default=0,
                null=True,
                verbose_name="\xdaltima Situa\xe7\xe3o (R$)",
                max_digits=18,
                decimal_places=2,
            ),
            preserve_default=True,
        ),
    ]
