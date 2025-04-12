# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Falta",
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
                ("texto", models.TextField(null=True, blank=True)),
                (
                    "anota",
                    models.BooleanField(
                        default=True, verbose_name="Gera Anota\xe7\xe3o"
                    ),
                ),
                ("data", models.DateField()),
                (
                    "justificada",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                (
                    "injustificada",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                (
                    "excedente",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                ("observacao", models.TextField(null=True, blank=True)),
            ],
            options={
                "ordering": ("-data",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Feriado",
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
                ("titulo", models.CharField(max_length=40)),
                ("data", models.DateField()),
                ("ano", models.IntegerField(blank=True)),
                (
                    "parte_dia",
                    models.IntegerField(
                        choices=[
                            (1, "MATUTINO"),
                            (2, "VESPERTINO"),
                            (3, "NOTURNO"),
                            (4, "DIA INTEIRO"),
                        ]
                    ),
                ),
                (
                    "tipo",
                    models.IntegerField(
                        choices=[
                            (1, "NACIONAL"),
                            (2, "ESTADUAL"),
                            (3, "MUNICIPAL"),
                            (4, "PONTO FACULTATIVO"),
                            (5, "LUTO"),
                        ]
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
