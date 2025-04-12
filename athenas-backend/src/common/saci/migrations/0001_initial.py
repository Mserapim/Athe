# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0011_auto_20160321_1634"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0017_auto_20160427_1523"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attendance",
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
                ("subject", models.CharField(max_length=200, verbose_name="assunto")),
                ("feedback", models.TextField(verbose_name="parecer", blank=True)),
                ("story", models.TextField(verbose_name="relato do cidad\xe3o")),
                (
                    "contains_represented",
                    models.BooleanField(
                        default=False, verbose_name="possui representado"
                    ),
                ),
                (
                    "competence_others",
                    models.BooleanField(
                        default=False, verbose_name="compet\xeancia do \xf3rg\xe3o"
                    ),
                ),
                ("content", models.TextField()),
                ("signed_content", models.TextField(null=True)),
                ("signed_at", models.DateTimeField(null=True)),
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
                    "department",
                    models.ForeignKey(
                        related_name="in_attendance_department",
                        verbose_name="departamento",
                        to="rh.OrgaoGeral",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "destination",
                    models.ForeignKey(
                        related_name="in_attendance_destination",
                        verbose_name="destina\xe7\xe3o",
                        to="rh.OrgaoGeral",
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
                    "person",
                    models.ForeignKey(
                        related_name="in_attendance",
                        verbose_name="pessoa",
                        to="rh.Pessoa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "protocol",
                    models.ForeignKey(
                        related_name="in_attendance_protocol",
                        verbose_name="protocolo",
                        to="protocolo.Protocolo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "represented",
                    models.ForeignKey(
                        related_name="in_attendance_represented",
                        verbose_name="representado",
                        to="rh.Pessoa",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "signed_by",
                    models.ForeignKey(
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Atendimento",
                "permissions": (("can_sign_attendance", "Pode assinar atendimento"),),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="AttendanceLegalSign",
            fields=[
                (
                    "legalsign_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="protocolo.LegalSign",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "attendance",
                    models.ForeignKey(
                        related_name="legal_signs",
                        to="saci.Attendance",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("protocolo.legalsign",),
        ),
        migrations.CreateModel(
            name="Typology",
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
                ("name", models.CharField(max_length=200, verbose_name="nome")),
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
                "ordering": ["name"],
                "verbose_name": "Tipologia de P\xfablico Alvo",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="attendance",
            name="typology",
            field=models.ForeignKey(
                related_name="in_attendance",
                verbose_name="Tipologia",
                to="saci.Typology",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
