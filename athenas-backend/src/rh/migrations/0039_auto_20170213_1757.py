# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0038_auto_20170127_1553"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeeworkplacehistory",
            name="commission",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="servidorlotacao",
            name="commission",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="anotacaogeral",
            name="tipo_documento",
            field=models.IntegerField(
                verbose_name="Tipo Documento",
                choices=[
                    (1, "ATO"),
                    (3, "PORTARIA"),
                    (4, "OF\xcdCIO"),
                    (5, "DESPACHO"),
                    (6, "TERMO"),
                    (7, "MEMORANDO"),
                    (8, "REQUERIMENTO"),
                    (9, "CONCESS\xc3O"),
                    (10, "ACORDO COOPERA\xc7\xc3O T\xc9CNICA"),
                    (12, "APOSTILA"),
                    (99, "OUTROS"),
                    (100, "DOCUMENTO DIGITAL"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="instance",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Inst\xe2ncia",
                choices=[(1, "PRIMEIRA INST\xc2NCIA"), (2, "SEGUNDA INST\xc2NCIA")],
            ),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="level_instance",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Entr\xe2ncia",
                choices=[
                    (1, "PRIMEIRA ENTR\xc2NCIA"),
                    (2, "SEGUNDA ENTR\xc2NCIA"),
                    (3, "TERCEIRA ENTR\xc2NCIA"),
                    (4, "PROCURADORIA"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="poder",
            field=models.IntegerField(
                default=5,
                choices=[
                    (1, "EXECUTIVO"),
                    (2, "LEGISLATIVO"),
                    (3, "JUDICI\xc1RIO"),
                    (4, "MINIST\xc9RIO P\xdaBLICO"),
                    (5, "DESCONHECIDO"),
                    (6, "TRIBUNAL DE CONTAS"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="dadobancario",
            name="tipo_conta",
            field=models.IntegerField(
                verbose_name="Tipo de Conta",
                choices=[(1, "CORRENTE"), (2, "POUPAN\xc7A"), (3, "SAL\xc1RIO")],
            ),
        ),
        migrations.AlterField(
            model_name="declaracaoatividade",
            name="turno",
            field=models.IntegerField(
                default=4,
                choices=[
                    (1, "Matutino"),
                    (2, "Vespertino"),
                    (3, "Noturno"),
                    (4, "Dia inteiro"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="dependencia",
            name="tipo",
            field=models.SmallIntegerField(
                default=1,
                choices=[
                    (1, "Imposto de Renda"),
                    (2, "PlanSa\xfade"),
                    (3, "Sal\xe1rio Fam\xedlia"),
                    (4, "Aux\xedlio Creche"),
                    (5, "Previd\xeancia"),
                    (6, "Aux\xedlio Especial"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="improvementandgraduatecnmp",
            name="nivel",
            field=models.IntegerField(
                verbose_name="N\xedvel",
                choices=[
                    (1, "Lato-Sensu"),
                    (2, "Mestrado"),
                    (3, "Doutorado"),
                    (4, "P\xf3s-Doutorado"),
                    (5, "Livre Doc\xeancia"),
                    (6, "Especializa\xe7\xe3o"),
                    (7, "Aperfei\xe7oamento Funcional"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="sexual_orientation",
            field=models.PositiveSmallIntegerField(
                default=5,
                null=True,
                verbose_name="Orienta\xe7\xe3o Sexual",
                blank=True,
                choices=[
                    (1, "Heterossexual"),
                    (2, "Homossexual"),
                    (3, "Bissexual"),
                    (4, "Assexual"),
                    (5, "N\xe3o Informada"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="publication_state",
            field=models.SmallIntegerField(
                default=1,
                choices=[
                    (1, "Em Aberto"),
                    (2, "P\xfablica\xe7\xe3o Solicitada"),
                    (3, "P\xfablica\xe7\xe3o Realizada"),
                    (4, "P\xfablica\xe7\xe3o Cancelada"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="tipo",
            field=models.IntegerField(
                verbose_name="Tipo de Publica\xe7\xe3o",
                choices=[
                    (1, "ATO"),
                    (2, "DECRETO"),
                    (3, "PORTARIA"),
                    (4, "OF\xcdCIO"),
                    (5, "DESPACHO"),
                    (6, "TERMO"),
                    (7, "MEMORANDO"),
                    (8, "REQUERIMENTO"),
                    (9, "CONCESS\xc3O"),
                    (10, "ACORDO COOPERA\xc7\xc3O T\xc9CNICA"),
                    (11, "LEI"),
                    (12, "APOSTILA"),
                    (14, "DECRETO LEGISLATIVO"),
                    (15, "RESOLU\xc7\xc3O"),
                    (16, "CIRCULAR"),
                    (17, "PROCESSO"),
                    (95, "DECLARA\xc7\xc3O DE ENTRADA EM ATIVIDADE"),
                    (96, "TERMO LOTA\xc7\xc3O"),
                    (97, "TERMO EXERC\xcdCIO"),
                    (98, "TERMO POSSE"),
                    (99, "OUTROS"),
                    (100, "DOCUMENTO DIGITAL"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="veiculo_publicacao",
            field=models.IntegerField(
                blank=True,
                null=True,
                verbose_name="Ve\xedculo Publica\xe7\xe3o",
                choices=[
                    (1, "DOE ACRE"),
                    (2, "DOE AMAPA"),
                    (3, "DOE AMAZONAS"),
                    (4, "DOE RORAIMA"),
                    (5, "DOE RONDONIA"),
                    (6, "DOE PARA"),
                    (7, "DOE TOCANTINS"),
                    (8, "DOE CEARA"),
                    (9, "DOE RIO GRANDE DO NORTE"),
                    (10, "DOE PERNAMBUCO"),
                    (11, "DOE PARAIBA"),
                    (12, "DOE SERGIPE"),
                    (13, "DOE BAHIA"),
                    (14, "DOE MARANHAO"),
                    (15, "DOE PIAUI"),
                    (16, "DOE MINAS GERAIS"),
                    (17, "DOE SAO PAULO"),
                    (18, "DOE ESPIRITO SANTO"),
                    (19, "DOE RIO DE JANEIRO"),
                    (21, "DOE PARANA"),
                    (22, "DOE SANTA CATARINA"),
                    (23, "DOE RIO GRANDE DO SUL"),
                    (24, "DOE MATO GROSSO DO SUL"),
                    (25, "DOE GOIAS"),
                    (26, "DOE DISTRITO FEDERAL"),
                    (27, "DOE MATO GROSSO"),
                    (28, "DIARIO JUSTICA"),
                    (29, "DIARIO JUSTICA ELEITORAL"),
                    (30, "DIARIO OFICIAL DA UNIAO"),
                    (31, "DIARIO OFICIAL DO MUNICIPIO DE PALMAS TO"),
                    (32, "REGISTRO CIVIL DAS PESSOAS NATURAIS"),
                    (33, "PLACAR"),
                    (34, "DI\xc1RIO ELETR\xd4NICO DO MPE"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="publishedworkscnmp",
            name="work_type",
            field=models.IntegerField(
                verbose_name="Tipo",
                choices=[
                    (1, "Artigo"),
                    (2, "Disserta\xe7\xe3o"),
                    (3, "Livro"),
                    (4, "Monografia"),
                    (5, "Peri\xf3dico"),
                    (6, "Relat\xf3rio"),
                    (7, "Registro em Anal"),
                    (8, "Tese"),
                ],
            ),
        ),
    ]
