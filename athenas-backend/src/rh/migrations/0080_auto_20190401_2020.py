# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0079_auto_20190130_1112"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profissionalsaude",
            name="conselho_regional",
        ),
        migrations.AddField(
            model_name="documento",
            name="class_organ",
            field=models.IntegerField(default=99, blank=True),
        ),
        migrations.AddField(
            model_name="movimentacaoposse",
            name="financial_effect_date",
            field=models.DateField(
                null=True, verbose_name="Data do Efeito Financeiro", blank=True
            ),
        ),
        migrations.AddField(
            model_name="movimentacaoposse",
            name="judicial_deposit",
            field=models.BooleanField(
                default=False, verbose_name="Pagamento realizado em ju\xc3\xadzo"
            ),
        ),
        migrations.AddField(
            model_name="movimentacaoposse",
            name="legal_amnesty_process",
            field=models.CharField(
                max_length=13,
                null=True,
                verbose_name="N\xfamero e Ano Lei Anistia",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="movimentacaoposse",
            name="number_process",
            field=models.CharField(
                max_length=20,
                null=True,
                verbose_name="N\xfamero do Processo Judicial",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="movimentacaorequisicao",
            name="category",
            field=models.IntegerField(
                default=301, verbose_name="Categoria eSocial origem"
            ),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="indicativo",
            field=models.CharField(
                default="S",
                max_length=1,
                choices=[
                    ("I", "INDEFINIDO"),
                    ("E", "ESTAGI\xc1RIO"),
                    ("M", "MEMBRO DO MINIST\xc9RIO P\xdaBLICO"),
                    ("P", "MILITAR"),
                    ("S", "SERVIDOR"),
                    ("T", "TERCEIRIZADO"),
                    ("V", "VOLUNT\xc1RIO"),
                    ("A", "JOVEM CIDAD\xc3O - APRENDIZ"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="tipo_lei_cargo",
            field=models.CharField(
                default="EF",
                max_length=2,
                choices=[
                    ("EF", "EFETIVO"),
                    ("CM", "COMISS\xc3O"),
                    ("FC", "FUN\xc7\xc3O DE CONFIAN\xc7A"),
                    ("AC", "ACORDO DE COOPERA\xc7\xc3O T\xc9CNICA"),
                    ("ES", "ESTAGI\xc1RIO"),
                    ("EL", "ELETIVO"),
                    ("TE", "TERCEIRIZADO"),
                    ("VL", "VOLUNT\xc1RIO"),
                    ("JC", "JOVEM CIDAD\xc3O - APRENDIZ"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="declaracaoatividade",
            name="activity_as",
            field=models.CharField(
                default="I",
                max_length=1,
                blank=True,
                choices=[
                    ("I", "INDEFINIDO"),
                    ("E", "ESTAGI\xc1RIO"),
                    ("M", "MEMBRO DO MINIST\xc9RIO P\xdaBLICO"),
                    ("P", "MILITAR"),
                    ("S", "SERVIDOR"),
                    ("T", "TERCEIRIZADO"),
                    ("V", "VOLUNT\xc1RIO"),
                    ("A", "JOVEM CIDAD\xc3O - APRENDIZ"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="movimentacaorequisicao",
            name="onus",
            field=models.IntegerField(
                default=2,
                verbose_name="\xd4nus",
                choices=[
                    (1, "ORIGEM"),
                    (2, "REQUISITANTE"),
                    (3, "Cedente e Cession\xe1rio"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="servidor",
            name="categoria_cache",
            field=models.CharField(
                default="SERVIDOR_QUADRO",
                max_length=40,
                choices=[
                    (
                        "SERVIDOR_EXTRA_REQUISITADO_AC",
                        "Servidor - Extraquadro - Acordo Coopera\xe7\xe3o T\xe9cnica sem \xf4nus",
                    ),
                    ("SERVIDOR_QUADRO", "Servidor - Quadro"),
                    (
                        "MEMBRO_1ENT",
                        "Membro - Promotor de Justi\xe7a 1\xaa Entr\xe2ncia",
                    ),
                    ("ESTAGIARIO", "Estagi\xe1rio"),
                    (
                        "MEMBRO_3ENT",
                        "Membro - Promotor de Justi\xe7a 3\xaa Entr\xe2ncia",
                    ),
                    ("SERVIDOR_EXTRAQUADRO", "Servidor - Extraquadro"),
                    (
                        "SERVIDOR_EXTRA_REQUISITADO_AC_ONUS",
                        "Servidor - Extraquadro - Acordo Coopera\xe7\xe3o T\xe9cnica com \xf4nus",
                    ),
                    ("MEMBRO", "Membro"),
                    ("VOLUNTARIO", "Volunt\xe1rio"),
                    (
                        "SERVIDOR_EXTRA_REQUISITADO_ONUS",
                        "Servidor - Extraquadro requisitado com \xf4nus",
                    ),
                    (
                        "MEMBRO_2ENT",
                        "Membro - Promotor de Justi\xe7a 2\xaa Entr\xe2ncia",
                    ),
                    (
                        "SERVIDOR_EXTRA_REQUISITADO",
                        "Servidor - Extraquadro requisitado",
                    ),
                    ("MEMBRO_PROCURADOR", "Membro - Procurador de Justi\xe7a"),
                    ("MEMBRO_SUBS", "Membro - Promotor de Justi\xe7a Substituto"),
                    ("JOVEM_CIDADAO", "Jovem Cidad\xe3o - Aprendiz"),
                    ("TERCEIRIZADO", "Terceirizado"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="servidor",
            name="matricula",
            field=models.IntegerField(
                help_text="Apenas n\xfameros",
                unique=True,
                verbose_name="Matr\xedcula",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="servidor",
            name="tipo",
            field=models.CharField(
                default="S",
                max_length=1,
                blank=True,
                choices=[
                    ("I", "INDEFINIDO"),
                    ("E", "ESTAGI\xc1RIO"),
                    ("M", "MEMBRO DO MINIST\xc9RIO P\xdaBLICO"),
                    ("P", "MILITAR"),
                    ("S", "SERVIDOR"),
                    ("T", "TERCEIRIZADO"),
                    ("V", "VOLUNT\xc1RIO"),
                    ("A", "JOVEM CIDAD\xc3O - APRENDIZ"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="servidor",
            name="type_by_possession",
            field=models.CharField(
                default="EFE",
                max_length=3,
                verbose_name="Tipo",
                blank=True,
                choices=[
                    ("EFE", "SERVIDOR EFETIVO"),
                    ("ECM", "SERVIDOR EFETIVO E COMISSIONADO"),
                    ("MBR", "MEMBRO"),
                    ("MEL", "MEMBRO COM CARGO ELETIVO"),
                    ("MCM", "MEMBRO COM CARGO COMISSIONADO"),
                    ("MEC", "MEMBRO COM CARGO ELETIVO E COMISSIONADO"),
                    ("CMS", "SERVIDOR COMISSIONADO"),
                    ("REQ", "SERVIDOR REQUISITADO"),
                    ("RCM", "SERVIDOR REQUISITADO COMISSIONADO"),
                    ("EST", "ESTAGI\xc1RIO"),
                    ("TCR", "TERCEIRIZADO"),
                    ("VOL", "VOLUNT\xc1RIO"),
                    ("CTR", "SERVIDOR CONTRATADO"),
                    ("EXT", "EXTERNO SEM V\xcdNCULO"),
                    ("SAP", "SERVIDOR EFETIVO APOSENTADO"),
                    ("MAP", "MEMBRO APOSENTADO"),
                    ("RFC", "SERVIDOR REQUISITADO COM FUN\xc7\xc3O"),
                    ("EFC", "SERVIDOR EFETIVO COM FUN\xc7\xc3O"),
                    ("JCA", "JOVEM CIDAD\xc3O - APRENDIZ"),
                    ("XXX", "DESCONHECIDO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="socialsecurityconfig",
            name="mass_segregation_plan",
            field=models.PositiveSmallIntegerField(
                default=1,
                choices=[
                    (1, "Plano previdenci\xe1rio ou \xfanico"),
                    (2, "Plano financeiro"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="tiposervidor",
            name="indicativo",
            field=models.CharField(
                default="S",
                max_length=1,
                choices=[
                    ("I", "INDEFINIDO"),
                    ("E", "ESTAGI\xc1RIO"),
                    ("M", "MEMBRO DO MINIST\xc9RIO P\xdaBLICO"),
                    ("P", "MILITAR"),
                    ("S", "SERVIDOR"),
                    ("T", "TERCEIRIZADO"),
                    ("V", "VOLUNT\xc1RIO"),
                    ("A", "JOVEM CIDAD\xc3O - APRENDIZ"),
                ],
            ),
        ),
    ]
