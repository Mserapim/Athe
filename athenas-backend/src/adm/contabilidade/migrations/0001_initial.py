# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mto", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Categoria",
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
                ("descricao", models.CharField(max_length=150)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="FonteRecurso",
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
                ("numero", models.CharField(unique=True, max_length=50)),
                ("descricao", models.CharField(max_length=150)),
                ("convenio", models.BooleanField(default=False)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="GrupoContabil",
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
                ("numero", models.IntegerField(unique=True)),
                ("descricao", models.CharField(max_length=150)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="NE",
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
                ("numero", models.CharField(unique=True, max_length=50)),
                ("data", models.DateTimeField(auto_now_add=True, null=True)),
                ("data_nota", models.DateField(null=True, blank=True)),
                (
                    "modalidade",
                    models.IntegerField(
                        choices=[(1, "ORDIN\xc1RIO"), (3, "ESTIMATIVA"), (5, "GLOBAL")]
                    ),
                ),
                (
                    "valor",
                    models.DecimalField(max_digits=16, decimal_places=2, blank=True),
                ),
            ],
            options={
                "ordering": ("-id", "numero"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PPAAcao",
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
                ("codigo", models.CharField(max_length=10)),
                (
                    "funcao",
                    models.CharField(max_length=10, verbose_name="Fun\xe7\xe3o"),
                ),
                (
                    "subfuncao",
                    models.CharField(max_length=10, verbose_name="Subfun\xe7\xe3o"),
                ),
                ("titulo", models.CharField(max_length=120)),
                ("cache_codigo", models.CharField(max_length=40, null=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PPAPrograma",
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
                ("codigo", models.CharField(max_length=10)),
                ("titulo", models.CharField(max_length=60)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PPARevisao",
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
                ("data_vigencia", models.DateField(null=True)),
                ("ano_inicio", models.SmallIntegerField()),
                ("ano_fim", models.SmallIntegerField()),
                ("ano_revisao", models.SmallIntegerField(null=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Produto",
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
                ("descricao", models.CharField(max_length=200)),
                ("quantidade", models.IntegerField()),
                ("fracao", models.DecimalField(max_digits=16, decimal_places=2)),
                (
                    "subitem",
                    models.ForeignKey(
                        related_name="produto",
                        to="mto.ElementoDespesaSubItem",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Unidade",
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
                ("sigla", models.CharField(max_length=6)),
                ("descricao", models.CharField(max_length=150)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="produto",
            name="unidade",
            field=models.ForeignKey(
                to="contabilidade.Unidade", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
