# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cif", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="debtsencumbrances",
            name="current_value",
            field=models.DecimalField(
                verbose_name="Situa\xe7\xe3o Atual (R$)",
                max_digits=18,
                decimal_places=5,
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
                decimal_places=5,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="property",
            name="current_value",
            field=models.DecimalField(
                verbose_name="Situa\xe7\xe3o Atual (R$)",
                max_digits=18,
                decimal_places=5,
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
                decimal_places=5,
            ),
            preserve_default=True,
        ),
    ]
