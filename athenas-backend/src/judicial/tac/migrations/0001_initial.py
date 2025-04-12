# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0025_auto_20160711_1502"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ged", "0003_auto_20151014_1609"),
        ("judicial", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Activity",
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
                ("description", models.TextField()),
                (
                    "time_type",
                    models.SmallIntegerField(
                        default=0,
                        null=True,
                        blank=True,
                        choices=[
                            (0, "N\xe3o informado"),
                            (1, "Dia"),
                            (2, "M\xeas"),
                            (3, "Ano"),
                        ],
                    ),
                ),
                ("time", models.IntegerField(null=True, blank=True)),
                (
                    "realized",
                    models.SmallIntegerField(
                        default=0,
                        null=True,
                        blank=True,
                        choices=[
                            (0, "Em Andamento"),
                            (1, "Cumprido"),
                            (2, "N\xe3o Cumprido"),
                            (3, "Executado"),
                        ],
                    ),
                ),
                (
                    "fine_value",
                    models.DecimalField(
                        null=True, max_digits=16, decimal_places=2, blank=True
                    ),
                ),
                (
                    "repair_value",
                    models.DecimalField(
                        null=True, max_digits=16, decimal_places=2, blank=True
                    ),
                ),
                (
                    "process_number_fine",
                    models.CharField(
                        default=b"", max_length=300, null=True, blank=True
                    ),
                ),
            ],
            options={
                "ordering": ("tac",),
                "db_table": "tac_activity",
                "permissions": (("activity_tac", "Vis\xe3o Atividade da TAC"),),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ActivityHistory",
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
                ("description", models.TextField()),
                (
                    "time_type",
                    models.SmallIntegerField(
                        null=True,
                        choices=[
                            (0, "N\xe3o informado"),
                            (1, "Dia"),
                            (2, "M\xeas"),
                            (3, "Ano"),
                        ],
                    ),
                ),
                ("time", models.IntegerField(null=True)),
                (
                    "realized",
                    models.SmallIntegerField(
                        null=True,
                        choices=[
                            (0, "Em Andamento"),
                            (1, "Cumprido"),
                            (2, "N\xe3o Cumprido"),
                            (3, "Executado"),
                        ],
                    ),
                ),
                (
                    "activity",
                    models.ForeignKey(
                        related_name="activity_history",
                        to="tac.Activity",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "author",
                    models.ForeignKey(
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
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
            ],
            options={
                "ordering": ("-created_at",),
                "db_table": "tac_activity_history",
                "permissions": (
                    ("activity_history_tac", "Vis\xe3o Hist\xf3rico Atividade da TAC"),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Document",
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
                    "title",
                    models.CharField(max_length=150, verbose_name="Document Title"),
                ),
                ("description", models.TextField()),
                (
                    "accepted",
                    models.SmallIntegerField(
                        default=0,
                        null=True,
                        blank=True,
                        choices=[
                            (0, "N\xe3o Informado"),
                            (1, "Cumprido"),
                            (2, "N\xe3o Cumprido"),
                        ],
                    ),
                ),
                (
                    "activity_document",
                    models.ForeignKey(
                        related_name="document_activity",
                        to="tac.Activity",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
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
                    "file_document",
                    models.ForeignKey(
                        related_name="+",
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
            ],
            options={
                "ordering": ("activity_document",),
                "db_table": "tac_document",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ManagementTAC",
            fields=[
                (
                    "partlawsuit_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("description", models.TextField()),
                ("considerations", models.TextField()),
                (
                    "date_signature",
                    models.DateField(
                        null=True, verbose_name="Data da Assinatura do TAC", blank=True
                    ),
                ),
                (
                    "author_signature",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "tac_manag_tac",
                "permissions": (("manager_tac", "Vis\xe3o Gest\xe3o de TAC"),),
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="Responsible",
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
                    "activity",
                    models.ForeignKey(
                        related_name="responsible_activity",
                        to="tac.Activity",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
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
                    "responsible_person",
                    models.ForeignKey(
                        related_name="responsible_person",
                        to="rh.Pessoa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("responsible_person",),
                "db_table": "tac_responsible",
                "permissions": (
                    ("responsible_tac", "Vis\xe3o Respos\xe1vel Atividade TAC"),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="activity",
            name="act_history",
            field=models.ForeignKey(
                related_name="history",
                blank=True,
                to="tac.ActivityHistory",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="activity",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="activity",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="activity",
            name="tac",
            field=models.ForeignKey(
                related_name="activities_tac",
                to="tac.ManagementTAC",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
