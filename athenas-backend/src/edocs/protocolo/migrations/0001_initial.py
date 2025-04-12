# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
import django.db.models.deletion
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Anexo",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Attachment",
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
                ("title", models.CharField(max_length=100)),
                ("observation", models.TextField()),
            ],
            options={
                "ordering": ("title",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="CompartilharCaixa",
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
            ],
            options={
                "db_table": "protocolo_comp_caixa",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="CompartilharProtocolo",
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
            ],
            options={
                "db_table": "protocolo_comp_prot",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Etiqueta",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                ("carimbo_tempo", models.DateTimeField(auto_now_add=True)),
                ("localidade", models.CharField(max_length=100)),
                ("orgao", models.CharField(max_length=100)),
                ("label_inferior", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Impressora",
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
                ("nome", models.CharField(max_length=100)),
                ("host", models.CharField(max_length=100)),
                ("port", models.IntegerField()),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Movimentacao",
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
                ("deferido", models.NullBooleanField()),
                ("parecer", models.TextField(null=True, blank=True)),
                ("encaminhado", models.BooleanField(default=False)),
                ("data_recebimento", models.DateTimeField(null=True, blank=True)),
                (
                    "data_encaminhamento",
                    models.DateTimeField(db_index=True, null=True, blank=True),
                ),
                ("passo", models.IntegerField(db_index=True)),
                ("urgente", models.BooleanField(default=False)),
                (
                    "data_finalizado",
                    models.DateTimeField(
                        default=None, null=True, db_index=True, blank=True
                    ),
                ),
            ],
            options={
                "ordering": ["data_encaminhamento"],
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PermissaoEdoc",
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
                ("nome", models.CharField(max_length=100)),
                ("codigo", models.CharField(max_length=6)),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Protocolo",
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
                ("assunto", models.CharField(max_length=255, db_index=True)),
                (
                    "protocolo_externo",
                    models.CharField(
                        db_index=True,
                        max_length=50,
                        null=True,
                        verbose_name="N\xfamero Externo",
                        blank=True,
                    ),
                ),
                (
                    "resumo",
                    models.TextField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MaxLengthValidator(4000)],
                    ),
                ),
                ("deferido", models.NullBooleanField()),
                ("encaminhado", models.BooleanField(default=False)),
                ("grupo", models.BooleanField(default=False)),
                ("habilitado", models.BooleanField(default=False)),
                ("codigo", models.CharField(unique=True, max_length=50, db_index=True)),
                (
                    "data_criacao",
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
                (
                    "serial",
                    models.CharField(
                        db_index=True, max_length=10, null=True, blank=True
                    ),
                ),
                ("excluido", models.BooleanField(default=False)),
                (
                    "chancela",
                    models.CharField(
                        default="0000",
                        max_length=30,
                        null=True,
                        db_index=True,
                        blank=True,
                    ),
                ),
                ("sigiloso", models.BooleanField(default=False)),
                (
                    "midia",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        db_index=True,
                        choices=[(1, "FAX"), (2, "CARTA"), (3, "EMAIL")],
                    ),
                ),
                (
                    "data_finalizado",
                    models.DateTimeField(
                        default=None, null=True, db_index=True, blank=True
                    ),
                ),
                ("com_workflow", models.BooleanField(default=False)),
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
                "permissions": (("has_general_protocol", "Tem protocolo geral."),),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Referencia",
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
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "movimentacao",
                    models.ForeignKey(
                        blank=True,
                        to="protocolo.Movimentacao",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "protocolo",
                    models.ForeignKey(
                        blank=True,
                        to="protocolo.Protocolo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="TipoAssunto",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
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
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="TipoDocumento",
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
                ("nome", models.CharField(max_length=100)),
                (
                    "descricao",
                    models.TextField(
                        null=True, verbose_name="Descri\xe7\xe3o", blank=True
                    ),
                ),
                ("habilita", models.BooleanField(default=False)),
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
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
    ]
