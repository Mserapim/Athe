# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0043_auto_20171010_0934"),
    ]

    operations = [
        migrations.AddField(
            model_name="marginconsignable",
            name="maximum_cet",
            field=models.DecimalField(
                default=5,
                verbose_name="CET m\xc3\xa1ximo",
                max_digits=19,
                decimal_places=2,
            ),
        ),
        migrations.AddField(
            model_name="marginconsignable",
            name="maximum_installment",
            field=models.PositiveSmallIntegerField(
                default=200, verbose_name="Prazo m\xc3\xa1ximo", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="correctionfactor",
            name="ref_difference_cache",
            field=models.CharField(
                default="",
                max_length=6,
                verbose_name="Identificador",
                db_index=True,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="correctionfactor",
            name="ref_payment_cache",
            field=models.CharField(
                default="",
                max_length=15,
                verbose_name="Identificador",
                db_index=True,
                blank=True,
            ),
        ),
    ]
