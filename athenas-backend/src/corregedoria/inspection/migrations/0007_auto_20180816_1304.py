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
        ("inspection", "0006_auto_20180624_1507"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeadlineRecommendationAttachments",
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
                ("description", models.CharField(max_length=2000)),
                (
                    "attached_file",
                    models.ForeignKey(
                        related_name="deadline_file",
                        verbose_name="Arquivo",
                        to="ged.Arquivo",
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
            ],
            options={
                "verbose_name": "Arquivo anexados na solicita\xe7\xe3o de dila\xe7\xe3o de prazo",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="deadlinerecommendation",
            name="decision_at",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="deadlinerecommendation",
            name="sent",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="deadlinerecommendation",
            name="signdecision_at",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="deadlinerecommendation",
            name="signdecision_by",
            field=models.ForeignKey(
                related_name="sign_by",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="recommendations",
            name="deadline_origin",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="recommendations",
            name="finalized",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="recommendations",
            name="finalized_at",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="processesforanalysisperformanceinaudiences",
            name="audience_type",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Tipo de Audi\xeancia",
                blank=True,
                choices=[
                    (1, "N\xe3o informado"),
                    (2, "Concilia\xe7\xe3o"),
                    (3, "Instru\xe7\xe3o"),
                    (4, "Julgamento"),
                    (5, "Instru\xe7\xe3o e Julgamento"),
                    (6, "Preliminar"),
                    (7, "Interrogat\xf3rio"),
                    (8, "Inquiri\xe7\xe3o"),
                    (9, "Diploma\xe7\xe3o"),
                    (10, "Justifica\xe7\xe3o"),
                    (11, "Apresenta\xe7\xe3o"),
                    (12, "Apresenta\xe7\xe3o/Remiss\xe3o"),
                    (13, "Audi\xeancias gerais da Inf\xe2ncia e Juventude"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="deadlinerecommendationattachments",
            name="deadlinerecommendation",
            field=models.ForeignKey(
                related_name="attachments",
                to="inspection.DeadlineRecommendation",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="deadlinerecommendationattachments",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
