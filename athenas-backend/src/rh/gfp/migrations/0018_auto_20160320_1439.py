# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("gfp", "0017_auto_20160316_1100"),
    ]

    operations = [
        migrations.CreateModel(
            name="CorrectionFactor",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "identifier",
                    models.CharField(
                        max_length=8, verbose_name="Identificador", db_index=True
                    ),
                ),
                (
                    "factor",
                    models.DecimalField(default=1, max_digits=19, decimal_places=8),
                ),
                (
                    "ref_payment_year",
                    models.PositiveSmallIntegerField(verbose_name="Ref. Pag. - ANO"),
                ),
                (
                    "ref_payment_month",
                    models.PositiveSmallIntegerField(verbose_name="Ref. Pag. - M\xcaS"),
                ),
                (
                    "ref_difference_year",
                    models.PositiveSmallIntegerField(verbose_name="Ref. Dif. - ANO"),
                ),
                (
                    "ref_difference_month",
                    models.PositiveSmallIntegerField(verbose_name="Ref. Dif. - M\xcaS"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": (
                    "identifier",
                    "ref_payment_year",
                    "ref_payment_month",
                    "ref_difference_year",
                    "ref_difference_month",
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name="correctionfactor",
            unique_together=set(
                [
                    (
                        "identifier",
                        "ref_payment_year",
                        "ref_payment_month",
                        "ref_difference_year",
                        "ref_difference_month",
                    )
                ]
            ),
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="correction_factor_identifier",
            field=models.CharField(
                max_length=8,
                null=True,
                verbose_name="Fator de corre\xe7\xe3o",
                db_index=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="paycheckdifferenceitem",
            name="correction_factor",
            field=models.DecimalField(default=1, max_digits=19, decimal_places=8),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="paycheckdifferenceitem",
            name="fixed_employer_contribution",
            field=models.DecimalField(default=0, max_digits=19, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="paycheckdifferenceitem",
            name="fixed_value",
            field=models.DecimalField(default=0, max_digits=19, decimal_places=2),
            preserve_default=True,
        ),
    ]
