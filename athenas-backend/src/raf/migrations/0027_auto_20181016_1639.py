# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0056_attached_render_extract"),
        ("raf", "0026_auto_20180629_1322"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataEExt",
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
                ("month", models.CharField(max_length=2, null=True, blank=True)),
                ("year", models.CharField(max_length=4, null=True, blank=True)),
                (
                    "proccess_number",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "date_movement",
                    models.DateTimeField(
                        null=True, verbose_name="Data da atividade", blank=True
                    ),
                ),
                (
                    "analisys",
                    models.PositiveSmallIntegerField(
                        default=0,
                        verbose_name="An\xe1lise",
                        choices=[
                            (0, "N\xe3o analisado"),
                            (1, "Processo classificado com sucesso"),
                            (2, "Sem promotoria registrada para o processo"),
                            (3, "N\xe3o encontrou question\xe1rio para o processo"),
                            (4, "N\xe3o encontrou linha para o processo"),
                            (5, "N\xe3o encontrou coluna para o processo"),
                            (6, "Sem classe registrada para o processo"),
                            (7, "Sem assunto registrado para o processo"),
                            (8, "Sem movimento registrado para o processo"),
                        ],
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="rh.Servidor",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "legalclass",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="judicial.LegalClass",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "legalmatter",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="judicial.LegalMatter",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "legalmovement",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="judicial.LegalClassification",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "location",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="rh.Lotacao",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["employee", "location", "date_movement"],
                "verbose_name": "DataEExt",
            },
        ),
        migrations.AlterField(
            model_name="historicraf",
            name="action",
            field=models.PositiveSmallIntegerField(
                default=1,
                verbose_name="A\xe7\xe3o",
                choices=[
                    (1, "Inser\xe7\xe3o"),
                    (2, "Abertura"),
                    (3, "Fechamento"),
                    (4, "Submiss\xe3o"),
                    (5, "Submiss\xe3o / Membro afastado"),
                    (6, "Tentativa Submiss\xe3o - RAF Fechado"),
                    (7, "Tentativa Submiss\xe3o - RAF j\xe1 submetido"),
                    (8, "Tentativa Submiss\xe3o - Sem permiss\xe3o de submiss\xe3o"),
                    (9, "Tentativa Submiss\xe3o - RAF Anterior N\xc3O SUBMETIDO"),
                    (10, "Tentativa Submiss\xe3o - Pedidos de Ajustes Pendentes"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="subitem",
            name="productivity",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Produtividade",
                choices=[
                    (1, "N\xe3o se aplica"),
                    (2, "Presteza  - Feitos Judiciais"),
                    (3, "Presteza  - Feitos Extrajudiciais"),
                    (4, "Presteza  - Atendimento tempestivo \xe0s determina\xe7\xf5es"),
                    (5, "Produtividade - Fator I - Pe\xe7as Iniciais"),
                    (6, "Produtividade - Fator I - Procedimentos Administrativos"),
                    (7, "Produtividade - Fator II - Pe\xe7as Judiciais"),
                    (8, "Produtividade - Fator II - Procedimentos Administrativos"),
                    (9, "Produtividade - Fator III"),
                    (10, "Produtividade - Fator IV - Audi\xeancias Judiciais"),
                    (
                        11,
                        "Produtividade - Fator IV - Aud. P\xfablicas ou Administrativas",
                    ),
                    (12, "Produtividade - Fator IV - J\xfaris"),
                    (13, "Atendimento ao P\xfablico"),
                    (14, "Cumula\xe7\xe3o de Atividades, Cargos e Fun\xe7\xf5es "),
                    (15, "Afastamento para participa\xe7\xe3o em cursos - DOUTORADO"),
                    (16, "Afastamento para participa\xe7\xe3o em cursos - MESTRADO"),
                    (17, "Carga hor\xe1ria em cursos - ESPECIALIZA\xc7\xc3O"),
                    (18, "Carga hor\xe1ria em cursos - APERFEI\xc7OAMENTO"),
                    (19, "Atua\xe7\xe3o em Comarca de Particular Dificuldade"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="typequiz",
            name="group",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Grupo",
                choices=[
                    (1, "JUDICIAL"),
                    (2, "EXTRAJUDICIAL"),
                    (3, "MILITAR JUDICIAL"),
                    (4, "MILITAR EXTRAJUDICIAL"),
                    (5, "N\xc3O PROCEDIMENTAL"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="typequiz",
            name="species",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Esp\xe9cie",
                choices=[
                    (1, "C\xcdVEL"),
                    (2, "INF\xc2NCIA E JUVENTUDE"),
                    (3, "CRIMINAL"),
                    (4, "ELEITORAL"),
                ],
            ),
        ),
    ]
