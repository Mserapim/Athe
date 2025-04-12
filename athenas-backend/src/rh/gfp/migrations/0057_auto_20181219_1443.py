# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0056_auto_20180920_1341"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="folhaevento",
            options={
                "ordering": [
                    "contracheque__folha",
                    "contracheque__servidor",
                    "evento__numero",
                    "reference_year",
                    "reference_month",
                    "info",
                ],
                "permissions": (
                    (
                        "can_validate_event_payroll",
                        "Validar eventos pendentes na folha de pagamento",
                    ),
                    (
                        "can_validate_event_internal_control",
                        "Validar eventos pendentes no controle interno",
                    ),
                ),
            },
        ),
        migrations.AlterField(
            model_name="folhaevento",
            name="servidor",
            field=models.ForeignKey(
                related_name="entries",
                blank=True,
                to="rh.Servidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="remunerationperiod",
            name="gratification",
            field=models.DecimalField(default=0, max_digits=20, decimal_places=6),
        ),
        migrations.AlterField(
            model_name="remunerationperiod",
            name="normal_gratification",
            field=models.DecimalField(default=0, max_digits=20, decimal_places=6),
        ),
        migrations.AlterField(
            model_name="remunerationperiod",
            name="normal_value",
            field=models.DecimalField(default=0, max_digits=20, decimal_places=6),
        ),
        migrations.AlterField(
            model_name="remunerationperiod",
            name="value",
            field=models.DecimalField(default=0, max_digits=20, decimal_places=6),
        ),
    ]
