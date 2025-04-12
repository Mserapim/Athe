# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Concurso",
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
                ("nome", models.CharField(max_length=60, verbose_name="Nome")),
                (
                    "dt_inicio",
                    models.DateField(
                        null=True, verbose_name="Data de inicio", blank=True
                    ),
                ),
                (
                    "dt_fim",
                    models.DateField(null=True, verbose_name="Data de fim", blank=True),
                ),
                (
                    "promovido_por",
                    models.IntegerField(
                        choices=[(1, "CESAF"), (2, "CESAF E TERCEIRO"), (3, "TERCEIRO")]
                    ),
                ),
                ("data_cadastro", models.DateTimeField(auto_now_add=True)),
                (
                    "publicar",
                    models.BooleanField(default=False, verbose_name="Publicar no site"),
                ),
                (
                    "descricao",
                    models.TextField(
                        null=True,
                        verbose_name="Descri\xe7\xe3o para o Site",
                        blank=True,
                    ),
                ),
                (
                    "slug",
                    models.SlugField(max_length=384, null=True, verbose_name="Slug"),
                ),
            ],
            options={
                "db_table": "concurso_concurso",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Inscricao",
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
                ("homologado", models.DateTimeField(null=True, blank=True)),
                ("recurso", models.BooleanField(default=False, db_index=True)),
                ("aprovado", models.NullBooleanField()),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="SelecaoEstagio",
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
                ("curso", models.CharField(max_length=128, verbose_name="Curso")),
                (
                    "faculdade",
                    models.CharField(max_length=384, verbose_name="Faculdade"),
                ),
                (
                    "matricula",
                    models.CharField(
                        max_length=80,
                        verbose_name="N\xc3\xbamero de Matr\xc3\xadcula",
                        db_index=True,
                    ),
                ),
                (
                    "ano_periodo",
                    models.CharField(max_length=8, verbose_name="Ano/Per\xc3\xadodo"),
                ),
                (
                    "ano_conclusao",
                    models.DateField(
                        verbose_name="Previs\xc3\xa3o de Conclus\xc3\xa3o",
                        db_index=True,
                    ),
                ),
                (
                    "disponibilidade",
                    models.IntegerField(
                        default=1,
                        null=True,
                        choices=[(1, "Manh\xc3\xa3"), (2, "Tarde")],
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Vaga",
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
                    "area",
                    models.CharField(
                        max_length=384, verbose_name="\xc3\x81rea", db_index=True
                    ),
                ),
                (
                    "quantidade",
                    models.IntegerField(verbose_name="Quantidade", db_index=True),
                ),
                (
                    "concurso",
                    models.ForeignKey(
                        related_name="vagas",
                        verbose_name="Concurso",
                        to="concurso.Concurso",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
