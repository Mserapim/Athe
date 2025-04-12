# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditableModel",
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
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                ("deleted", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="created_by_user",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="modified_by_user",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Choice",
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
                (
                    "app_label",
                    models.CharField(
                        max_length=60, verbose_name="Aplicativo", db_index=True
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=60, verbose_name="Nome da constante", db_index=True
                    ),
                ),
                ("label", models.CharField(max_length=60, verbose_name="Label")),
                ("value", models.SmallIntegerField(verbose_name="Valor")),
                ("cache_path", models.CharField(max_length=120, db_index=True)),
            ],
            options={
                "ordering": ("cache_path", "value"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ClassCode",
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
                ("slug", models.CharField(max_length=128, unique=True, null=True)),
                ("path", models.CharField(max_length=128, unique=True, null=True)),
                ("title", models.CharField(max_length=128, blank=True)),
                ("description", models.CharField(max_length=128, null=True)),
                ("name_object", models.CharField(max_length=128)),
                (
                    "typeof",
                    models.CharField(
                        default="CALCULO",
                        max_length=20,
                        db_index=True,
                        choices=[
                            ("CALCULO", "C\xc3\xa1lculos para FOPAG"),
                            ("LOADER", "Carregadores de arquivos"),
                        ],
                    ),
                ),
            ],
            options={
                "ordering": ("path",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Configuration",
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
                (
                    "application",
                    models.SlugField(unique=True, max_length=60, verbose_name="Chave"),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Item",
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
                ("key", models.SlugField(max_length=40, verbose_name="Chave")),
                (
                    "type",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Tipo",
                        choices=[
                            (0, "Texto"),
                            (1, "N\xfamerico"),
                            (2, "Sim ou N\xe3o"),
                        ],
                    ),
                ),
                (
                    "value",
                    models.TextField(null=True, verbose_name="Valor", blank=True),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="configuration",
            name="itens",
            field=models.ManyToManyField(to="standard.Item", null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="choice",
            unique_together=set(
                [("app_label", "name", "value"), ("app_label", "name", "label")]
            ),
        ),
    ]
