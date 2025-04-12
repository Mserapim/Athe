# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0073_datamigration_type_street"),
    ]

    operations = [
        migrations.AddField(
            model_name="lotacao",
            name="organizational_classification",
            field=models.IntegerField(
                default=1, verbose_name="Classifica\xe7\xe3o do Organograma"
            ),
        ),
        migrations.AlterField(
            model_name="digitaldocument",
            name="document_type",
            field=models.IntegerField(
                verbose_name="Tipo de Documento",
                choices=[
                    (56, "COMPROVANTE VOTA\xc7\xc3O 2018 - GERAL"),
                    (55, "COMPROVANTE VOTA\xc7\xc3O 2018 - SUPLEMENTAR"),
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
                    (51, "CERTID\xc3O DE CASAMENTO/DIV\xd3RCIO"),
                    (52, "COMPROVANTE DE ENDERE\xc7O"),
                    (53, "TERMO DE CUSTODIA DE MENOR"),
                    (54, "UNIAO ESTAVEL"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="endereco",
            name="tipo_logradouro",
            field=models.IntegerField(
                verbose_name="Tipo do Logradouro",
                choices=[
                    (1, "AVENIDA"),
                    (2, "PRA\xc7A"),
                    (3, "VIELA"),
                    (4, "PONTO - SERA EXCLUIDO"),
                    (5, "VIADUTO"),
                    (7, "OUTROS - SERA EXCLUIDO"),
                    (8, "RUA"),
                    (9, "QUADRA"),
                    (100, "EXTERIOR"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="movimentacaodesligamento",
            name="tipo_desligamento",
            field=models.IntegerField(
                default=1,
                verbose_name="Tipo de Desligamento",
                choices=[
                    (1, "EXONERA\xc7\xc3O EFETIVO"),
                    (2, "EXONERA\xc7\xc3O COMISSIONADO"),
                    (3, "EXONERA\xc7\xc3O ESTABILIZADO"),
                    (4, "APOSENTADORIA POR INVALIDEZ"),
                    (5, "APOSENTADORIA VOLUNT\xc1RIA"),
                    (6, "POSSE EM OUTRO CARGO"),
                    (7, "FALECIMENTO"),
                    (8, "RESCIS\xc3O"),
                    (9, "DEMISS\xc3O"),
                    (10, "RESERVA REFORMA"),
                    (11, "DISPONIBILIDADE"),
                    (12, "PROMO\xc7\xc3O/REMO\xc7\xc3O"),
                    (13, "FIM REQUISI\xc7\xc3O/ACORDO COOPERA\xc7\xc3O"),
                    (14, "APOSENTADORIA COMPULS\xd3RIA"),
                    (15, "APOSENTADORIA ESPECIAL"),
                    (16, "APOSENTADORIA POR TEMPO DE CONTRIBUI\xc7\xc3O"),
                    (17, "APOSENTADORIA POR IDADE"),
                    (18, "REDISTRIBUI\xc7\xc3O"),
                    (19, "REVERS\xc3O DE REINTEGRA\xc7\xc3O"),
                    (20, "FIM DE MANDATO"),
                ],
            ),
        ),
    ]
