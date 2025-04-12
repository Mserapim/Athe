# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CategoriaEconomica",
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
                ("numero", models.IntegerField()),
                ("descricao", models.CharField(max_length=150)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ElementoDespesa",
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
                ("numero", models.IntegerField()),
                ("descricao", models.CharField(max_length=150)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ElementoDespesaSubItem",
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
                ("numero", models.IntegerField()),
                ("descricao", models.CharField(max_length=150)),
                # Parametro "on_delete" adicionado. (Django 2)
                (
                    "elemento_despesa",
                    models.ForeignKey(
                        to="mto.ElementoDespesa", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="GrupoDespesa",
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
                ("numero", models.IntegerField()),
                ("descricao", models.CharField(max_length=150)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ModalidadeAplicacao",
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
                ("numero", models.IntegerField()),
                ("descricao", models.CharField(max_length=150)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="NaturezaDespesa",
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
                    "numero_cache",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "categoria_economica",
                    models.ForeignKey(
                        to="mto.CategoriaEconomica", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                # Parametro "on_delete" adicionado. (Django 2)
                (
                    "elemento_despesa",
                    models.ForeignKey(
                        to="mto.ElementoDespesa", on_delete=models.CASCADE
                    ),
                ),
                # Parametro "on_delete" adicionado. (Django 2)
                (
                    "grupo_despesa",
                    models.ForeignKey(to="mto.GrupoDespesa", on_delete=models.CASCADE),
                ),
                (
                    "modalidade_aplicacao",
                    models.ForeignKey(
                        to="mto.ModalidadeAplicacao", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": [
                    "grupo_despesa__numero",
                    "modalidade_aplicacao__numero",
                    "categoria_economica__numero",
                    "elemento_despesa__numero",
                ],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="naturezadespesa",
            unique_together=set(
                [
                    (
                        "grupo_despesa",
                        "modalidade_aplicacao",
                        "categoria_economica",
                        "elemento_despesa",
                    )
                ]
            ),
        ),
    ]
