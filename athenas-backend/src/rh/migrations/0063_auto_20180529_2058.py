# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0062_auto_20180309_1645"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeeworkplacehistory",
            name="ordinance",
            field=models.BooleanField(default=False, verbose_name="Por portaria"),
        ),
        migrations.AddField(
            model_name="movimentacaosubstituicao",
            name="ordinance",
            field=models.BooleanField(default=False, verbose_name="Por portaria"),
        ),
        migrations.AddField(
            model_name="servidorlotacao",
            name="ordinance",
            field=models.BooleanField(default=False, verbose_name="Por portaria"),
        ),
        migrations.AlterField(
            model_name="digitaldocument",
            name="document_type",
            field=models.IntegerField(
                verbose_name="Tipo de Documento",
                choices=[
                    (1, "T\xcdTULO DE ELEITOR"),
                    (2, "CNH"),
                    (3, "CTPS"),
                    (5, "NIS"),
                    (6, "PIS/PASEP"),
                    (9, "RESERVISTA"),
                    (10, "CONSELHO PROFISSIONAL"),
                    (11, "RIC"),
                    (12, "RNE"),
                    (13, "CPF"),
                    (14, "RG"),
                    (15, "PASSAPORTE"),
                    (50, "CERTID\xc3O DE NASCIMENTO"),
                    (51, "CERTID\xc3O CASAMENTO/DIV\xd3RCIO"),
                    (52, "COMPROVANTE DE ENDERE\xc7O"),
                    (53, "TERMO DE CUSTODIA DE MENOR"),
                    (54, "COMPROVANTE UNIAO ESTAVEL"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="digitaldocumentnaturalperson",
            name="document_natural_person",
            field=models.ForeignKey(
                related_name="digital_document_natural_person",
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="Documento da Pessoa F\xedsica",
                blank=True,
                to="rh.Documento",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="documento",
            name="dados_especificos",
            field=models.ManyToManyField(
                related_name="documentos",
                verbose_name="Dados Espec\xedficos",
                to="rh.DocsDadosEspecificos",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="documento",
            name="tipo_documento",
            field=models.IntegerField(
                verbose_name="Tipo de Documento",
                choices=[
                    (1, "T\xcdTULO DE ELEITOR"),
                    (2, "CNH"),
                    (3, "CTPS"),
                    (5, "NIS"),
                    (6, "PIS/PASEP"),
                    (7, "IPSEP"),
                    (8, "INSS"),
                    (9, "RESERVISTA"),
                    (10, "CONSELHO PROFISSIONAL"),
                    (11, "RIC"),
                    (12, "RNE"),
                    (13, "CPF"),
                    (14, "RG"),
                    (15, "PASSAPORTE"),
                    (54, "UNIAO ESTAVEL"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="documento",
            field=models.ManyToManyField(
                related_name="naturalpersons", to="rh.Documento", blank=True
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
                    (7, "DOE TOCANTINS"),
                    (34, "DI\xc1RIO ELETR\xd4NICO DO MPE"),
                    (31, "DIARIO OFICIAL DO MUNICIPIO DE PALMAS TO"),
                    (30, "DIARIO OFICIAL DA UNIAO"),
                    (1, "DOE ACRE"),
                    (2, "DOE AMAPA"),
                    (3, "DOE AMAZONAS"),
                    (4, "DOE RORAIMA"),
                    (5, "DOE RONDONIA"),
                    (6, "DOE PARA"),
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
                    (32, "REGISTRO CIVIL DAS PESSOAS NATURAIS"),
                    (33, "PLACAR"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="replacement",
            name="substitute",
            field=models.ForeignKey(
                related_name="replacement_substitutes",
                on_delete=django.db.models.deletion.PROTECT,
                to="rh.Lotacao",
            ),
        ),
    ]
