# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("judicial", "0056_attached_render_extract"),
    ]

    operations = [
        migrations.CreateModel(
            name="Pouch",
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
                ("pouch_number", models.SmallIntegerField(null=True, blank=True)),
                ("pouch_year", models.SmallIntegerField(null=True, blank=True)),
                (
                    "cache_number",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                ("signed_at", models.DateTimeField(null=True, blank=True)),
                ("content", models.TextField(null=True, blank=True)),
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
                    "from_location",
                    models.ForeignKey(
                        related_name="+",
                        to="judicial.ExecutionOrgan",
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
                    "signed_by",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "to_location",
                    models.ForeignKey(
                        related_name="+",
                        to="judicial.ExecutionOrgan",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("-signed_by", "-pouch_year", "-pouch_number"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PouchLawsuit",
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
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "lawsuit",
                    models.ForeignKey(
                        related_name="as_pouches_items",
                        to="judicial.OutCourtLawsuit",
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
                    "movement_part",
                    models.ForeignKey(
                        related_name="as_item_of_pouches",
                        blank=True,
                        to="judicial.PartLawsuit",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "pouch",
                    models.ForeignKey(
                        related_name="items",
                        to="judicial.Pouch",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="GerencialRemittenceInternal",
            fields=[],
            options={
                "proxy": True,
            },
            bases=("judicial.remittanceinternal",),
        ),
        migrations.CreateModel(
            name="PouchedRemittance",
            fields=[],
            options={
                "proxy": True,
            },
            bases=("judicial.remittanceinternal",),
        ),
        migrations.AlterUniqueTogether(
            name="pouchlawsuit",
            unique_together=set([("pouch", "lawsuit")]),
        ),
    ]
