# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("gfp", "0053_auto_20180917_1501"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConfigEvent",
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
                    "max_quantity",
                    models.DecimalField(
                        default=0,
                        verbose_name="Quantidade m\xe1xima",
                        max_digits=10,
                        decimal_places=6,
                    ),
                ),
                (
                    "quantity",
                    models.DecimalField(
                        null=True,
                        verbose_name="Quantidade",
                        max_digits=10,
                        decimal_places=6,
                        blank=True,
                    ),
                ),
                (
                    "percentage",
                    models.DecimalField(
                        null=True,
                        verbose_name="Porcentagem",
                        max_digits=10,
                        decimal_places=6,
                        blank=True,
                    ),
                ),
                (
                    "base_value",
                    models.DecimalField(
                        null=True,
                        verbose_name="Valor base",
                        max_digits=10,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                (
                    "floor",
                    models.DecimalField(
                        null=True,
                        verbose_name="Teto",
                        max_digits=10,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                (
                    "ceiling",
                    models.DecimalField(
                        null=True,
                        verbose_name="Piso",
                        max_digits=10,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                (
                    "evaluate_difference",
                    models.BooleanField(
                        default=False, verbose_name="Avaliar diferen\xe7a?"
                    ),
                ),
                (
                    "separate_for_competencies",
                    models.BooleanField(
                        default=True, verbose_name="Separar por compet\xeancias?"
                    ),
                ),
                (
                    "separate_for_info_event",
                    models.BooleanField(
                        default=False, verbose_name="Separar por info?"
                    ),
                ),
                (
                    "config_value",
                    models.CharField(
                        default="",
                        max_length=400,
                        verbose_name="Cofigura\xe7\xe3o - valor",
                        blank=True,
                    ),
                ),
                (
                    "automated",
                    models.BooleanField(default=False, verbose_name="Autom\xe1tico"),
                ),
                (
                    "inverted_calculation",
                    models.BooleanField(
                        default=False, verbose_name="C\xe1lculo invertido"
                    ),
                ),
                (
                    "start_validity",
                    models.DateField(verbose_name="In\xedcio vig\xeancia"),
                ),
                (
                    "end_validity",
                    models.DateField(
                        null=True, verbose_name="Fim vig\xeancia", blank=True
                    ),
                ),
                (
                    "calculation",
                    models.ForeignKey(
                        related_name="config_events",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="C\xe1lculo",
                        blank=True,
                        to="standard.ClassCode",
                        null=True,
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
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterField(
            model_name="evento",
            name="incide_sobre",
            field=models.ManyToManyField(
                related_name="_evento_incide_sobre_+",
                verbose_name="Incide sobre",
                to="gfp.Evento",
            ),
        ),
        migrations.AddField(
            model_name="configevent",
            name="event",
            field=models.ForeignKey(
                related_name="configs",
                verbose_name="Evento",
                to="gfp.Evento",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="configevent",
            name="focuses_on",
            field=models.ManyToManyField(
                related_name="aplica_em", verbose_name="Incide sobre", to="gfp.Evento"
            ),
        ),
        migrations.AddField(
            model_name="configevent",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
