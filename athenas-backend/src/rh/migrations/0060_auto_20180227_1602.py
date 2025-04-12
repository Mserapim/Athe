# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ged", "0004_auto_20180201_1933"),
        ("rh", "0059_auto_20171226_1707"),
    ]

    operations = [
        migrations.CreateModel(
            name="DigitalDocument",
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
                    "name",
                    models.CharField(
                        default="", max_length=100, verbose_name="Nome", blank=True
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "document_type",
                    models.IntegerField(verbose_name="Tipo de Documento"),
                ),
                (
                    "date_start",
                    models.DateField(auto_now_add=True, verbose_name="Data in\xedcio"),
                ),
                (
                    "date_end",
                    models.DateField(null=True, verbose_name="Data fim", blank=True),
                ),
                ("active", models.BooleanField(default=False, verbose_name="Ativo")),
            ],
            options={
                "ordering": ("-date_end",),
                "verbose_name": "Documento Digital",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="cargo",
            name="requires_profissional_council",
            field=models.BooleanField(
                default=False, verbose_name="Exige Conselho Profissional"
            ),
        ),
        migrations.AddField(
            model_name="telefone",
            name="description",
            field=models.CharField(
                default="", max_length=80, verbose_name="Descri\xe7\xe3o"
            ),
        ),
        migrations.AddField(
            model_name="telefone",
            name="main",
            field=models.BooleanField(default=False, verbose_name="Principal"),
        ),
        migrations.CreateModel(
            name="DigitalDocumentNaturalPerson",
            fields=[
                (
                    "digitaldocument_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.DigitalDocument",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "document_natural_person",
                    models.ForeignKey(
                        related_name="digital_document_natural_person",
                        verbose_name="Documento da Pessoa F\xedsica",
                        to="rh.Documento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "verbose_name": "Documento Digital da Pessoa F\xedsica",
            },
            bases=("rh.digitaldocument",),
        ),
        migrations.AddField(
            model_name="digitaldocument",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="digitaldocument",
            name="employee",
            field=models.ForeignKey(
                related_name="digital_document",
                verbose_name="Servidor",
                blank=True,
                to="rh.Servidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="digitaldocument",
            name="file",
            field=models.ForeignKey(
                related_name="digital_document",
                verbose_name="Arquivo",
                to="ged.Arquivo",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="digitaldocument",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
