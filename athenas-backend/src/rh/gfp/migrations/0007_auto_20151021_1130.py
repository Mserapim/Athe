# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0006_auto_20150928_0828"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="evento",
            name="config_difference_contrib",
        ),
        migrations.RemoveField(
            model_name="evento",
            name="config_difference_value",
        ),
        migrations.RemoveField(
            model_name="evento",
            name="config_return_contrib",
        ),
        migrations.RemoveField(
            model_name="evento",
            name="config_return_value",
        ),
        migrations.AddField(
            model_name="evento",
            name="config_value",
            field=models.CharField(
                default="",
                max_length=400,
                verbose_name="Cofigura\xc3\xa7\xc3\xa3o - valor",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="description",
            field=models.CharField(
                default="", max_length=400, verbose_name="Descri\xe7\xe3o"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="diff_type",
            field=models.CharField(
                default="", max_length=3, verbose_name="Tipo", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="entries",
            field=models.ManyToManyField(
                to="gfp.FolhaEvento", through="gfp.PaycheckDifferenceItem"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="reference_month",
            field=models.PositiveSmallIntegerField(
                default=1, verbose_name="M\xeas Refer\xeancia", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="reference_year",
            field=models.PositiveSmallIntegerField(
                default=2015, verbose_name="Ano Refer\xeancia", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="paycheckdifferenceitem",
            name="paid_employer_contribution",
            field=models.DecimalField(default=0, max_digits=19, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="paycheckdifferenceitem",
            name="paid_value",
            field=models.DecimalField(default=0, max_digits=19, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="paycheckdifference",
            name="status",
            field=models.PositiveSmallIntegerField(
                default=1,
                verbose_name="Situa\xe7\xe3o",
                choices=[
                    (1, "ABERTO"),
                    (2, "PAGANDO PARCELADO"),
                    (3, "PARCIALMENTE PAGO"),
                    (4, "PAGO SEM INFORMA\xc7\xc3O"),
                    (5, "PAGO"),
                    (6, "IGNORADO"),
                ],
            ),
            preserve_default=True,
        ),
    ]
