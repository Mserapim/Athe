# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
import datetime
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("gfp", "0008_auto_20151021_1205"),
    ]

    operations = [
        migrations.CreateModel(
            name="MarginConsignable",
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
                    "identification",
                    models.CharField(
                        max_length=32, verbose_name="Margem", db_index=True
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        default="", max_length=64, verbose_name="T\xedtulo"
                    ),
                ),
                (
                    "percentage",
                    models.DecimalField(default=0, max_digits=19, decimal_places=2),
                ),
                ("active", models.BooleanField(default=False, verbose_name="Ativo?")),
                (
                    "start_validity",
                    models.DateField(
                        default=datetime.date(1900, 1, 1),
                        verbose_name="In\xc3\xadcio vig\xc3\xaancia",
                    ),
                ),
                (
                    "consignables",
                    models.ManyToManyField(
                        related_name="margins_base",
                        verbose_name="Eventos base",
                        to="gfp.Evento",
                    ),
                ),
                (
                    "consigneds",
                    models.ManyToManyField(
                        related_name="margins_consigneds",
                        verbose_name="Consignados",
                        to="gfp.Evento",
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
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "type_of_payroll",
                    models.ForeignKey(
                        related_name="margins",
                        verbose_name="Tipo de Folha",
                        to="gfp.FolhaTipo",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("identification",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="MarginPaycheck",
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
                    "total_value",
                    models.DecimalField(default=0, max_digits=19, decimal_places=2),
                ),
                (
                    "value",
                    models.DecimalField(default=0, max_digits=19, decimal_places=2),
                ),
                (
                    "margin",
                    models.ForeignKey(
                        related_name="margin_paychecks",
                        verbose_name="Margem",
                        to="gfp.MarginConsignable",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "paycheck",
                    models.ForeignKey(
                        related_name="margin_paychecks",
                        verbose_name="Contracheque",
                        to="gfp.ContraCheque",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="marginpaycheck",
            unique_together=set([("paycheck", "margin")]),
        ),
        migrations.AlterModelOptions(
            name="movimentacaoprogressao",
            options={
                "ordering": [
                    "-data_inicio_vigencia",
                    "-movimentacao_posse__servidor__pessoa_fisica__nome",
                ],
                "verbose_name": "Movimenta\xe7\xe3o Pessoal",
            },
        ),
        migrations.AlterField(
            model_name="loadedentryhistory",
            name="entry",
            field=models.OneToOneField(
                related_name="loaded_entry",
                null=True,
                verbose_name="Lan\xe7amento",
                to="gfp.FolhaEvento",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
