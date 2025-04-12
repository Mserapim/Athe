# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        # ('rh', '0080_auto_20190322_1939'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cirdir", "0007_auto_20190315_1238"),
    ]

    operations = [
        migrations.CreateModel(
            name="Evaluator",
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
                ("name", models.TextField(null=True, blank=True)),
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
                "verbose_name": "Cadastro de Avaliadores - Setor de Sa\xfade",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="health",
            name="evaluated",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="health",
            name="evaluation",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="location",
            field=models.ManyToManyField(
                related_name="srdir_health_locations",
                null=True,
                to="rh.Lotacao",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="health",
            name="medical_license_family_support",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="medical_license_higher_3_days_last_2_years",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="medical_license_less_3_days_last_year",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="pause_for_rest",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="sitting_time",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="strength_at_work",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="uses_2_screens",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="health",
            name="evaluator",
            field=models.ForeignKey(
                related_name="healths",
                blank=True,
                to="cirdir.Evaluator",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
