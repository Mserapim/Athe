# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0070_auto_20181127_1854"),
    ]

    operations = [
        migrations.AlterField(
            model_name="unidadeadministrativa",
            name="tax_classification",
            field=models.IntegerField(
                verbose_name="Classifica\xe7\xe3o tribut\xe1ria",
                choices=[
                    (
                        1,
                        "Empresa enquadrada no regime de tributa\xe7\xe3o Simples Nacional com tributa\xe7\xe3o previdenci\xe1riasubstitu\xedda",
                    ),
                    (
                        2,
                        "Empresa enquadrada no regime de tributa\xe7\xe3o Simples Nacional com tributa\xe7\xe3o previdenci\xe1ria n\xe3osubstitu\xedda",
                    ),
                    (
                        3,
                        "Empresa enquadrada no regime de tributa\xe7\xe3o Simples Nacional com tributa\xe7\xe3o previdenci\xe1riasubstitu\xedda e n\xe3o substitu\xedda",
                    ),
                    (4, "MEI - Micro Empreendedor Individual"),
                    (6, "Agroind\xfastria"),
                    (8, "Cons\xf3rcio Simplificado de Produtores Rurais"),
                    (9, "\xd3rg\xe3o Gestor de M\xe3o de Obra"),
                    (10, "Entidade Sindical a que se refere a Lei 12.023/2009"),
                    (
                        11,
                        "Associa\xe7\xe3o Desportiva que mant\xe9m Clube de Futebol Profissional",
                    ),
                    (
                        13,
                        "Banco, caixa econ\xf4mica, sociedade de cr\xe9dito, financiamento e investimento e demais empresas relacionadas no par\xe1grafo",
                    ),
                    (
                        14,
                        "Sindicatos em geral, exceto aquele classificado no c\xf3digo [10]",
                    ),
                    (21, "Pessoa F\xedsica, exceto Segurado Especial"),
                    (22, "Segurado Especial"),
                    (
                        60,
                        "Miss\xe3o Diplom\xe1tica ou Reparti\xe7\xe3o Consular de carreira estrangeira",
                    ),
                    (70, "Empresa de que trata o Decreto 5.436/2005"),
                    (
                        80,
                        "Entidade Beneficente de Assist\xeancia Social isenta de contribui\xe7\xf5es sociais",
                    ),
                    (
                        85,
                        "Administra\xe7\xe3o Direta da Uni\xe3o, Estados, Distrito Federal e Munic\xedp\xedos; Autarquias e Funda\xe7\xf5es P\xfablicas",
                    ),
                    (99, "Pessoas Jur\xeddicas em Geral"),
                ],
            ),
        ),
    ]
