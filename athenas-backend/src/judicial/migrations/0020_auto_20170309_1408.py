# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings
from django.core.management import call_command
import os

FIXTURES = ("fixtures/0021-choices-worker_reminder.json",)


def up(apps, schema_editor):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "judicial", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def down(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("judicial", "0019_create_interested"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkerReminder",
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
                ("observation", models.TextField(blank=True)),
                ("resolved", models.BooleanField(default=False)),
                ("deadline", models.DateField(null=True)),
                ("priority", models.SmallIntegerField()),
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
                    "part",
                    models.ForeignKey(
                        related_name="worker_reminder",
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "receiver",
                    models.ForeignKey(
                        related_name="worker_reminder",
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterField(
            model_name="judicialdiligence",
            name="who_type",
            field=models.SmallIntegerField(
                blank=True,
                choices=[
                    (1, "Interessado"),
                    (2, "Apontado"),
                    (3, "Testemunha"),
                    (4, "\xd3rg\xe3o de Execu\xe7\xe3o"),
                    (5, "\xd3rg\xe3o P\xfablico"),
                    (6, "Empresa Privada"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="manifestation",
            name="who_type",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Interessado"),
                    (2, "Apontado"),
                    (3, "Testemunha"),
                    (4, "\xd3rg\xe3o de Execu\xe7\xe3o"),
                    (5, "\xd3rg\xe3o P\xfablico"),
                    (6, "Empresa Privada"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="ordinace",
            name="type_ordinace",
            field=models.SmallIntegerField(
                choices=[
                    (2, "INQU\xc9RITO CIVIL P\xdaBLICO"),
                    (3, "PROCEDIMENTO PREPARAT\xd3RIO"),
                    (4, "PROCEDIMENTO INVESTIGATORIO CRIMINAL"),
                    (7, "PROCEDIMENTO ADMINISTRATIVO"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="rejectionfact",
            name="rejection_fact_type",
            field=models.SmallIntegerField(
                choices=[
                    (1, "N\xe3o presente a legitimidade do MP"),
                    (
                        2,
                        "O fato n\xe3o constitui viola\xe7\xe3o de direito e interesses difuso",
                    ),
                    (3, "O fato j\xe1 se encontrar solucionado"),
                    (4, "O fato j\xe1 \xe9 objeto de investiga\xe7\xe3o ou ACP"),
                    (
                        5,
                        "N\xe3o traz ind\xedcios m\xednimos para in\xedcio de investiga\xe7\xe3o",
                    ),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="rejectionfact",
            name="type_ordinace",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (2, "INQU\xc9RITO CIVIL P\xdaBLICO"),
                    (3, "PROCEDIMENTO PREPARAT\xd3RIO"),
                    (4, "PROCEDIMENTO INVESTIGATORIO CRIMINAL"),
                    (7, "PROCEDIMENTO ADMINISTRATIVO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="owner",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="slug",
            field=models.CharField(
                max_length=40, verbose_name="Abrevia\xe7\xe3o", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="title",
            field=models.CharField(max_length=40, verbose_name="T\xedtulo", blank=True),
        ),
        migrations.AlterField(
            model_name="tag",
            name="work_place",
            field=models.ForeignKey(
                related_name="tags",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Lotacao",
                null=True,
            ),
        ),
        migrations.RunPython(up, down),
    ]
