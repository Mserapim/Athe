# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("gfp", "0005_auto_20150923_0750"),
    ]

    operations = [
        migrations.CreateModel(
            name="LoadedEntryHistory",
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
                    "typeof",
                    models.CharField(
                        default="GFP", max_length=64, verbose_name="Tipo", db_index=True
                    ),
                ),
                (
                    "identification",
                    models.CharField(
                        default="",
                        max_length=64,
                        verbose_name="Identificador",
                        db_index=True,
                    ),
                ),
                (
                    "line_text",
                    models.CharField(default="", max_length=400, verbose_name="Linha"),
                ),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        default=1,
                        verbose_name="Status",
                        choices=[
                            (1, "Carregado com sucesso"),
                            (2, "N\xe3o carregado - matr\xedcula n\xe3o encontrada"),
                            (3, "N\xe3o carregado - servidor exonerado"),
                            (4, "N\xe3o carregado - servidor afastado"),
                            (5, "N\xe3o carregado - evento inexistente"),
                            (6, "Erro - lan\xe7amento inexistente no contracheque"),
                            (9, "N\xe3o carregado - erro desconhecido"),
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
                (
                    "entry",
                    models.OneToOneField(
                        related_name="loaded_entry",
                        null=True,
                        verbose_name="Lan\xc3\xa7amento",
                        to="gfp.FolhaEvento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
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
                    "payroll",
                    models.ForeignKey(
                        related_name="loaded_entries",
                        verbose_name="Folha",
                        to="gfp.Folha",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name="loadedentryhistory",
            unique_together=set([("payroll", "identification", "entry", "typeof")]),
        ),
    ]
