# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("gfp", "0040_auto_20170418_1505"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaycheckDifferenceConfig",
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
                    "initial_installment",
                    models.PositiveSmallIntegerField(default=1, verbose_name="Parcela"),
                ),
                (
                    "final_installment",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="Parcela", blank=True
                    ),
                ),
                (
                    "value",
                    models.DecimalField(default=0, max_digits=19, decimal_places=4),
                ),
                (
                    "employer_contribution",
                    models.DecimalField(default=0, max_digits=19, decimal_places=2),
                ),
                (
                    "typeof",
                    models.PositiveSmallIntegerField(
                        default=1,
                        verbose_name="Base",
                        choices=[
                            (1, "Valor Fixo"),
                            (2, "Percentual"),
                            (3, "Sal. m\xednimo"),
                        ],
                    ),
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
            ],
            options={
                "ordering": ("difference", "initial_installment"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="expected_end_month",
            field=models.PositiveSmallIntegerField(
                default=1, verbose_name="M\xeas Refer\xeancia", blank=True
            ),
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="expected_end_year",
            field=models.PositiveSmallIntegerField(
                default=2017, verbose_name="Ano Refer\xeancia", blank=True
            ),
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="focuses_on",
            field=models.ManyToManyField(
                related_name="focuses_by_differences",
                verbose_name="Incide sobre",
                to="gfp.Evento",
            ),
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="payment_event",
            field=models.ForeignKey(
                related_name="differences_payment",
                verbose_name="Evento de pagamento",
                blank=True,
                to="gfp.Evento",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="source_differences",
            field=models.BooleanField(
                default=True, verbose_name="Gestor de diferen\xc3\xa7as?"
            ),
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="total_employer_contribution",
            field=models.DecimalField(default=0, max_digits=19, decimal_places=2),
        ),
        migrations.AddField(
            model_name="paycheckdifference",
            name="total_value",
            field=models.DecimalField(default=0, max_digits=19, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="movimentacaoprogressao",
            name="data_vigencia",
            field=models.DateField(verbose_name="Data Vig\xeancia", blank=True),
        ),
        migrations.AlterField(
            model_name="previdencia",
            name="identifier",
            field=models.PositiveSmallIntegerField(
                default=1, verbose_name="Identificador"
            ),
        ),
        migrations.AddField(
            model_name="paycheckdifferenceconfig",
            name="difference",
            field=models.ForeignKey(
                related_name="differences_config",
                to="gfp.PaycheckDifference",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="paycheckdifferenceconfig",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
