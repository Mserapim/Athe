# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings
from django.core.management import call_command

import os

fixtures_files = (
    ("fixtures/00-menu.json", "Could not load usefulday menu options."),
    ("fixtures/01-choices.json", "Could not load usefulday choices."),
    ("fixtures/02-profiles.json", "Could not load usefulday profiles."),
)


def load_choices_fixtures_and_permissions_fixtures(apps, schema_editor):

    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Loading fixtures...")
    try:
        for fixture, err_message in fixtures_files:
            filepath = os.path.join(BASE_DIR, "common", "usefulday", fixture)
            print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
            call_command("loaddata", filepath)
    except Exception:
        print("ERR: %s" % err_message)


def reverse_load_choices_fixtures_and_permissions_fixtures(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0066_auto_20180830_1454"),
        ("ged", "0004_auto_20180201_1933"),
    ]

    operations = [
        migrations.CreateModel(
            name="NonWorkingDay",
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
                    "description",
                    models.CharField(max_length=50, verbose_name="Descri\xe7\xe3o"),
                ),
                ("is_partial", models.BooleanField(default=False)),
                ("start_date", models.DateTimeField(verbose_name="Data inicial")),
                (
                    "end_date",
                    models.DateTimeField(
                        null=True, verbose_name="Data final", blank=True
                    ),
                ),
                (
                    "abrangency",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "Nacional"), (2, "Estadual"), (3, "Municipal")]
                    ),
                ),
                (
                    "kind",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "Feriado"),
                            (2, "Ponto Facultativo"),
                            (3, "Suspens\xe3o"),
                        ]
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
                    "document",
                    models.ForeignKey(
                        related_name="nonworkingdays",
                        blank=True,
                        to="ged.Arquivo",
                        null=True,
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
                    "places",
                    models.ManyToManyField(
                        related_name="nonworkingdays",
                        verbose_name="Cidades",
                        to="rh.Localidade",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ParseNonWorkingDay",
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
                ("parse_date", models.DateTimeField(verbose_name="Data")),
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
                    "nonworkingday",
                    models.ForeignKey(
                        related_name="parsenonworkingdays",
                        to="usefulday.NonWorkingDay",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "place",
                    models.ForeignKey(
                        related_name="parsenonworkingdays",
                        blank=True,
                        to="rh.Localidade",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name="parsenonworkingday",
            unique_together=set([("nonworkingday", "parse_date", "place")]),
        ),
        migrations.RunPython(
            load_choices_fixtures_and_permissions_fixtures,
            reverse_load_choices_fixtures_and_permissions_fixtures,
        ),
    ]
