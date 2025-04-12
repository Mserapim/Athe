# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        # ('rh', '0079_auto_20190126_0019'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("inspection", "0020_auto_20190121_1822"),
    ]

    operations = [
        migrations.CreateModel(
            name="StructureExternalPeoples",
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
                ("name", models.CharField(max_length=300)),
                ("function", models.CharField(max_length=300)),
                ("category", models.CharField(max_length=300)),
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
                    "inspection",
                    models.ForeignKey(
                        related_name="+",
                        to="inspection.Inspection",
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
                    "personal_movement",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="rh.MovimentacaoPessoal",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Registro de Pessoal Externo do Org\xe3o Inspecionado, n\xe3o cadastrado no Athenas",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
    ]
