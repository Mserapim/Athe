# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BandScoreTable",
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
                ("label", models.CharField(max_length=250)),
                ("initial_value", models.SmallIntegerField(null=True, blank=True)),
                ("end_value", models.SmallIntegerField(null=True, blank=True)),
                ("score", models.SmallIntegerField()),
                ("active", models.BooleanField(default=True)),
                ("observation", models.TextField(null=True, blank=True)),
            ],
            options={
                "verbose_name": "Faixas para tabela de pontua\xe7\xe3o",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ConfigProductivity",
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
                    "productivity",
                    models.IntegerField(
                        verbose_name="Fator Produtividade",
                        choices=[
                            (1, "N\xe3o se aplica"),
                            (2, "Fator I"),
                            (3, "Fator II"),
                            (4, "Fator III"),
                            (5, "Fator IV"),
                        ],
                    ),
                ),
                (
                    "score_table",
                    models.IntegerField(verbose_name="Tabela de C\xe1lculo"),
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
            ],
            options={
                "ordering": ["productivity"],
                "verbose_name": "Tabela de configura\xe7\xe3o  Produtividade / Score Table",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ConfigScoreTable",
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
                ("ordination", models.CharField(max_length=250)),
                (
                    "score_table",
                    models.IntegerField(verbose_name="Tabela de C\xe1lculo"),
                ),
                ("active", models.BooleanField(default=True)),
                ("initial_validity", models.DateField(null=True, blank=True)),
                ("final_validity", models.DateField(null=True, blank=True)),
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
                "ordering": ["active"],
                "verbose_name": "Tabela de configura\xe7\xe3o dos c\xe1lculos de pontua\xe7\xe3o",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="bandscoretable",
            name="configscoretable",
            field=models.ForeignKey(
                related_name="+",
                to="corregedoria.ConfigScoreTable",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="bandscoretable",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="bandscoretable",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
