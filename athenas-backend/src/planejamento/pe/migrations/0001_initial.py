# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Analise",
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
                    "data",
                    models.DateField(
                        null=True, verbose_name="Data de Refer\xeancia", blank=True
                    ),
                ),
                (
                    "tendencia",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Tend\xeancia",
                        choices=[(0, "ALTA"), (1, "EST\xc1VEL"), (2, "BAIXA")],
                    ),
                ),
                (
                    "analise",
                    models.CharField(
                        max_length=4000,
                        null=True,
                        verbose_name="An\xe1lise",
                        blank=True,
                    ),
                ),
                (
                    "recomendacoes",
                    models.CharField(
                        max_length=4000,
                        null=True,
                        verbose_name="Recomenda\xe7\xf5es",
                        blank=True,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="AnaliseIndicador",
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
                    "data",
                    models.DateField(
                        null=True, verbose_name="Data de Refer\xeancia", blank=True
                    ),
                ),
                (
                    "tendencia",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Tend\xeancia",
                        choices=[(0, "ALTA"), (1, "EST\xc1VEL"), (2, "BAIXA")],
                    ),
                ),
                (
                    "analise",
                    models.CharField(
                        max_length=4000,
                        null=True,
                        verbose_name="An\xe1lise",
                        blank=True,
                    ),
                ),
                (
                    "recomendacoes",
                    models.CharField(
                        max_length=4000,
                        null=True,
                        verbose_name="Recomenda\xe7\xf5es",
                        blank=True,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="AndamentoProjeto",
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
                ("data", models.DateField(null=True, verbose_name="Data", blank=True)),
                (
                    "concluido",
                    models.CharField(max_length=50, verbose_name="Conclu\xeddo"),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Indicador",
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
                    "nome",
                    models.CharField(unique=True, max_length=200, verbose_name="Nome"),
                ),
                (
                    "descricao",
                    models.CharField(max_length=4000, verbose_name="Descri\xe7\xe3o"),
                ),
                (
                    "tipo",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Tipo",
                        choices=[
                            (0, "PONTUAL"),
                            (1, "CUMULATIVO"),
                            (2, "AGUARDANDO DEFINI\xc7\xc3O"),
                        ],
                    ),
                ),
                (
                    "peso",
                    models.IntegerField(null=True, verbose_name="Peso", blank=True),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="IndicadorMeta",
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
                ("data", models.DateField(null=True, verbose_name="Data", blank=True)),
                (
                    "valor",
                    models.DecimalField(
                        verbose_name="Valor", max_digits=10, decimal_places=4
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="IndicadorValor",
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
                ("data", models.DateField(null=True, verbose_name="Data", blank=True)),
                (
                    "valor",
                    models.DecimalField(
                        verbose_name="Valor", max_digits=10, decimal_places=4
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Objetivo",
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
                    "nome",
                    models.CharField(unique=True, max_length=200, verbose_name="Nome"),
                ),
                (
                    "descricao",
                    models.CharField(
                        unique=True, max_length=4000, verbose_name="Descri\xe7\xe3o"
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Periodo",
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
                    "nome",
                    models.CharField(unique=True, max_length=200, verbose_name="Nome"),
                ),
                ("dias", models.IntegerField(verbose_name="Dias")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Planejamento",
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
                    "descricao",
                    models.CharField(
                        unique=True, max_length=200, verbose_name="Descri\xe7\xe3o"
                    ),
                ),
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data para In\xedcio", blank=True
                    ),
                ),
                (
                    "data_termino",
                    models.DateField(
                        null=True, verbose_name="Data para T\xe9rmino", blank=True
                    ),
                ),
                (
                    "metodo_analise",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="M\xe9todo para An\xe1lise",
                        choices=[(0, "MELHOR CASO"), (1, "PIOR CASO")],
                    ),
                ),
                (
                    "limite_alta",
                    models.IntegerField(verbose_name="Limite inferior para ALTA"),
                ),
                (
                    "limite_baixa",
                    models.IntegerField(verbose_name="Limite superior para BAIXA"),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Projeto",
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
                    "nome",
                    models.CharField(unique=True, max_length=200, verbose_name="Nome"),
                ),
                (
                    "descricao",
                    models.CharField(
                        max_length=4000,
                        null=True,
                        verbose_name="Descri\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data para In\xedcio", blank=True
                    ),
                ),
                (
                    "data_termino",
                    models.DateField(
                        null=True, verbose_name="Data para T\xe9rmino", blank=True
                    ),
                ),
                (
                    "status",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Status",
                        choices=[
                            (0, "N\xc3O INICIADO"),
                            (1, "ABERTO"),
                            (2, "BLOQUEADO"),
                            (3, "FECHADO"),
                            (4, "FECHADO PELO CLIENTE"),
                        ],
                    ),
                ),
                (
                    "andamento",
                    models.IntegerField(
                        null=True, verbose_name="Andamento", blank=True
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
