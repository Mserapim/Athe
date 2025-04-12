# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("raf", "0019_subitem_productivity"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricRAF",
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
                    "action",
                    models.PositiveSmallIntegerField(
                        default=1,
                        verbose_name="A\xe7\xe3o",
                        choices=[
                            (1, "Cria\xe7\xe3o"),
                            (2, "Abertura"),
                            (3, "Fechamento"),
                            (4, "Submiss\xe3o"),
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
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "raf",
                    models.ForeignKey(
                        related_name="historics",
                        to="raf.FunctionalActivityReport",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Hist\xf3rico do RAF",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
    ]
