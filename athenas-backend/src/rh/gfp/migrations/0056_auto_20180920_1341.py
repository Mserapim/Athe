# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0068_datamigration_config"),
        ("gfp", "0055_datamigration_event"),
    ]

    operations = [
        migrations.CreateModel(
            name="RemunerationBase",
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
                (
                    "identifier",
                    models.CharField(max_length=10, verbose_name="Identificador"),
                ),
                ("link", models.CharField(max_length=2, verbose_name="Tipo")),
                (
                    "salary",
                    models.PositiveIntegerField(
                        null=True, verbose_name="Refer\xeancia Sal\xe1rio"
                    ),
                ),
                (
                    "base_gratification",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "base_value",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "percentage",
                    models.BooleanField(default=False, verbose_name="Porcentagem"),
                ),
                (
                    "onus",
                    models.BooleanField(default=False, verbose_name="\xc3\x94nus"),
                ),
                (
                    "employee",
                    models.ForeignKey(to="rh.Servidor", on_delete=models.CASCADE),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
        ),
        migrations.CreateModel(
            name="RemunerationPeriod",
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
                ("start", models.DateField(verbose_name="In\xedcio do Per\xedodo")),
                ("end", models.DateField(verbose_name="Final do Per\xedodo")),
                (
                    "gratification",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "value",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "normal_gratification",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "normal_value",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                ("days", models.PositiveIntegerField(default=0, verbose_name="Dias")),
                (
                    "period",
                    models.ForeignKey(
                        to="gfp.Periodo", null=True, on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "remuneration",
                    models.ForeignKey(
                        related_name="periods",
                        default=None,
                        to="gfp.RemunerationBase",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("start", "end"),
            },
        ),
        migrations.RemoveField(
            model_name="configevent",
            name="config_value",
        ),
        migrations.RemoveField(
            model_name="configevent",
            name="evaluate_difference",
        ),
        migrations.RemoveField(
            model_name="configevent",
            name="separate_for_competencies",
        ),
        migrations.RemoveField(
            model_name="configevent",
            name="separate_for_info_event",
        ),
        migrations.RemoveField(
            model_name="evento",
            name="automatico",
        ),
        migrations.RemoveField(
            model_name="evento",
            name="calculo",
        ),
        migrations.RemoveField(
            model_name="evento",
            name="calculo_invertido",
        ),
        migrations.RemoveField(
            model_name="evento",
            name="incide_sobre",
        ),
        migrations.RemoveField(
            model_name="evento",
            name="piso",
        ),
        migrations.RemoveField(
            model_name="evento",
            name="porcentagem",
        ),
        migrations.RemoveField(
            model_name="evento",
            name="quantidade",
        ),
        migrations.RemoveField(
            model_name="evento",
            name="quantidade_max",
        ),
        migrations.RemoveField(
            model_name="evento",
            name="teto",
        ),
        migrations.RemoveField(
            model_name="evento",
            name="valor_base",
        ),
        migrations.AddField(
            model_name="extrapaymentperiod",
            name="gratification",
            field=models.BooleanField(
                default=False, verbose_name="Aplica-se \xe0 gratifica\xe7\xe3o"
            ),
        ),
        migrations.AddField(
            model_name="extrapaymentperiod",
            name="main_salary",
            field=models.BooleanField(
                default=True, verbose_name="Aplica-se \xe0 remunera\xe7\xe3o principal"
            ),
        ),
    ]
