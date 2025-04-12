# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0069_auto_20181121_1904"),
    ]

    operations = [
        migrations.AlterField(
            model_name="unidadeadministrativa",
            name="legal_nature",
            field=models.IntegerField(
                verbose_name="Natureza jur\xeddica",
                choices=[
                    (1015, "\xd3rg\xe3o P\xfablico do Poder Executivo Federal"),
                    (
                        1023,
                        "\xd3rg\xe3o P\xfablico do Poder Executivo Estadual ou do Distrito Federal",
                    ),
                    (1031, "\xd3rg\xe3o P\xfablico do Poder Executivo Municipal"),
                    (1040, "\xd3rg\xe3o P\xfablico do Poder Legislativo Federal"),
                    (
                        1058,
                        "\xd3rg\xe3o P\xfablico do Poder Legislativo Estadual ou do Distrito Federal",
                    ),
                    (1066, "\xd3rg\xe3o P\xfablico do Poder Legislativo Municipal"),
                    (1074, "\xd3rg\xe3o P\xfablico do Poder Judici\xe1rio Federal"),
                    (1082, "\xd3rg\xe3o P\xfablico do Poder Judici\xe1rio Estadual"),
                    (1104, "Autarquia Federal"),
                    (1112, "Autarquia Estadual ou do Distrito Federal"),
                    (1120, "Autarquia Municipal"),
                    (1139, "Funda\xe7\xe3o P\xfablica de Direito P\xfablico Federal"),
                    (
                        1147,
                        "Funda\xe7\xe3o P\xfablica de Direito P\xfablico Estadual ou do Distrito Federal",
                    ),
                    (1155, "Funda\xe7\xe3o P\xfablica de Direito P\xfablico Municipal"),
                    (1163, "\xd3rg\xe3o P\xfablico Aut\xf4nomo Federal"),
                    (
                        1171,
                        "\xd3rg\xe3o P\xfablico Aut\xf4nomo Estadual ou do Distrito Federal",
                    ),
                    (1180, "\xd3rg\xe3o P\xfablico Aut\xf4nomo Municipal"),
                    (1198, "Comiss\xe3o Polinacional"),
                    (1201, "Fundo P\xfablico"),
                    (
                        1210,
                        "Cons\xf3rcio P\xfablico de Direito P\xfablico (Associa\xe7\xe3o P\xfablica)",
                    ),
                    (1228, "Cons\xf3rcio P\xfablico de Direito Privado"),
                    (1236, "Estado ou Distrito Federal"),
                    (1244, "Munic\xedpio"),
                    (1252, "Funda\xe7\xe3o P\xfablica de Direito Privado Federal"),
                    (
                        1260,
                        "Funda\xe7\xe3o P\xfablica de Direito Privado Estadual ou do Distrito Federal",
                    ),
                    (1279, "Funda\xe7\xe3o P\xfablica de Direito Privado Municipal"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="unidadeadministrativa",
            name="subtetus_reference",
            field=models.IntegerField(
                verbose_name="Poder que se refere o subteto",
                choices=[
                    (1, "Executivo"),
                    (2, "Judici\xe1rio"),
                    (3, "Legislativo"),
                    (9, "Todos os poderes"),
                ],
            ),
        ),
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
                    (7, "Produtor Rural Pessoa Jur\xeddica"),
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
