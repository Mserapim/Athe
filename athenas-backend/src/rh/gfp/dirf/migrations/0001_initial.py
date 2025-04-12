# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Diaria",
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
                ("data", models.DateField()),
                ("valor", models.DecimalField(max_digits=11, decimal_places=2)),
            ],
            options={
                "db_table": "rh_vw_diarias",
                "managed": False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Declaracao",
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
                ("nome", models.CharField(max_length=10, null=True)),
                ("ano_base", models.IntegerField(null=True)),
                ("retificadora", models.IntegerField(blank=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Demonstrativo",
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
                    "qnt_meses",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                (
                    "rendimento",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                (
                    "rendimento_molestia",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                (
                    "previdencia_oficial",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                (
                    "previdencia_privada",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                (
                    "pensao_alimenticia",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                (
                    "imposto_retido",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                (
                    "parcela_isenta",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                (
                    "ajuda_custo",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                (
                    "pensao_aposentado",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                (
                    "lucro_dividendo",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                (
                    "servico_prestado",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                (
                    "idenizacao",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                (
                    "outros",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                ("outros_descricao", models.CharField(max_length=120, null=True)),
                (
                    "decimoterceiro",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                (
                    "decimoterceiro_imposto",
                    models.DecimalField(null=True, max_digits=12, decimal_places=2),
                ),
                ("decimoterceiro_outro", models.CharField(max_length=60, null=True)),
                (
                    "informacao_complementar",
                    models.CharField(max_length=200, null=True),
                ),
                ("data_geracao", models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Dialect",
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
                ("nome", models.CharField(unique=True, max_length=60, blank=True)),
                ("engine", models.CharField(max_length=100, null=True)),
                (
                    "identificador_layout",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="DirfResumos",
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
                ("ano", models.SmallIntegerField()),
                ("mes", models.SmallIntegerField()),
                (
                    "valor",
                    models.DecimalField(default=0.0, max_digits=11, decimal_places=2),
                ),
                (
                    "tipo",
                    models.CharField(default=b"DIARIA", max_length=20, db_index=True),
                ),
            ],
            options={
                "db_table": "dirf_resumos",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="NaturezaRendimento",
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
                ("codigo", models.CharField(unique=True, max_length=4)),
                ("titulo", models.CharField(max_length=300, null=True)),
                ("descricao", models.TextField()),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Token",
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
                ("nome", models.CharField(max_length=60)),
                ("slug", models.CharField(max_length=60, blank=True)),
                (
                    "id_receita",
                    models.CharField(
                        max_length=30, verbose_name="Identificador do Registro"
                    ),
                ),
                (
                    "tipo",
                    models.IntegerField(
                        null=True, choices=[(1, b"RENDIMENTO"), (2, b"DESPESA")]
                    ),
                ),
                (
                    "dialect",
                    models.ForeignKey(
                        related_name="tokens",
                        to="dirf.Dialect",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
