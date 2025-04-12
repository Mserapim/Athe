# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Licitacao",
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
                    "modalidade",
                    models.IntegerField(
                        choices=[
                            (1, "CONCORR\xcaNCIA"),
                            (2, "CARTA CONVITE"),
                            (3, "PREG\xc3O ELETR\xd4NICO"),
                            (4, "PREG\xc3O PRESENCIAL"),
                            (5, "TOMADA DE PRE\xc7O"),
                        ]
                    ),
                ),
                (
                    "registro_preco",
                    models.BooleanField(
                        default=False, verbose_name="Registro de pre\xe7o"
                    ),
                ),
                ("numero", models.CharField(max_length=100, verbose_name="N\xfamero")),
                (
                    "data_realizacao",
                    models.DateTimeField(
                        null=True, verbose_name="Data de realiza\xe7\xe3o", blank=True
                    ),
                ),
                ("data_cadastro", models.DateTimeField(auto_now_add=True, null=True)),
                ("arquivado", models.BooleanField(default=False)),
                ("finalizado", models.BooleanField(default=False)),
                ("contrato", models.BooleanField(default=False)),
                ("homologada", models.NullBooleanField()),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Participante",
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
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ProdutoVencedor",
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
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PublicacaoLicitacao",
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
                ("objeto", models.TextField(null=True, blank=True)),
                ("interno", models.BooleanField(default=False)),
                ("ano", models.CharField(max_length=4, verbose_name="Ano", blank=True)),
                (
                    "veiculo_publicacao",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Ve\xedculo Publica\xe7\xe3o",
                        choices=[
                            (31, "DIARIO OFICIAL DO MUNICIPIO DE PALMAS TO"),
                            (30, "DIARIO OFICIAL DA UNIAO"),
                            (28, "DIARIO JUSTICA"),
                            (29, "DIARIO JUSTICA ELEITORAL"),
                            (1, "DOE ACRE"),
                            (2, "DOE AMAPA"),
                            (3, "DOE AMAZONAS"),
                            (13, "DOE BAHIA"),
                            (8, "DOE CEARA"),
                            (26, "DOE DISTRITO FEDERAL"),
                            (18, "DOE ESPIRITO SANTO"),
                            (25, "DOE GOIAS"),
                            (6, "DOE PARA"),
                            (21, "DOE PARANA"),
                            (11, "DOE PARAIBA"),
                            (10, "DOE PERNAMBUCO"),
                            (15, "DOE PIAUI"),
                            (27, "DOE MATO GROSSO"),
                            (24, "DOE MATO GROSSO DO SUL"),
                            (14, "DOE MARANHAO"),
                            (16, "DOE MINAS GERAIS"),
                            (19, "DOE RIO DE JANEIRO"),
                            (9, "DOE RIO GRANDE DO NORTE"),
                            (23, "DOE RIO GRANDE DO SUL"),
                            (4, "DOE RORAIMA"),
                            (5, "DOE RONDONIA"),
                            (22, "DOE SANTA CATARINA"),
                            (17, "DOE SAO PAULO"),
                            (12, "DOE SERGIPE"),
                            (7, "DOE TOCANTINS"),
                            (32, "REGISTRO CIVIL DAS PESSOAS NATURAIS"),
                            (33, "PLACAR"),
                        ],
                    ),
                ),
                (
                    "numero_publicacao",
                    models.CharField(
                        max_length=22,
                        null=True,
                        verbose_name="N\xfamero Publica\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "data_publicacao",
                    models.DateField(
                        null=True, verbose_name="Data da Publica\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "data_expedicao",
                    models.DateField(
                        verbose_name="Data de expedi\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "tipo",
                    models.IntegerField(
                        choices=[
                            (1, "ATA DE REGISTRO DE PRE\xc7OS"),
                            (2, "AVISO"),
                            (3, "EDITAL"),
                            (4, "ESCLARECIMENTO"),
                            (5, "IMPUGNA\xc7\xc3O"),
                            (6, "HOMOLOGA\xc7\xc3O"),
                        ]
                    ),
                ),
                (
                    "natureza",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        choices=[(1, "ADIADO"), (2, "PRORROGADO"), (3, "REMARCADO")],
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
