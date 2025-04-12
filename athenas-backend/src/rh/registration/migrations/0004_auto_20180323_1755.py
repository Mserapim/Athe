# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0003_auto_20180228_1543"),
    ]

    operations = [
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
                    (51, "CERTID\xc3O DE CASAMENTO"),
                    (52, "COMPROVANTE DE ENDERE\xc7O"),
                    (53, "TERMO DE CUSTODIA DE MENOR"),
                    (54, "TERMO DE UNIAO ESTAVEL"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="digitaldocument",
            name="state",
            field=models.IntegerField(
                default=1,
                verbose_name="Estado de processamento",
                choices=[
                    (1, "N\xc3O PROCESSADO"),
                    (2, "PROCESSADO"),
                    (3, "N\xc3O VALIDADO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="forminformation",
            name="state",
            field=models.IntegerField(
                default=1,
                blank=True,
                verbose_name="Estado",
                choices=[
                    (1, "EDI\xc7\xc3O DO SERVIDOR"),
                    (2, "ENVIADO AO DGPFP"),
                    (3, "RECEBIDO DGPFP"),
                    (4, "VALIDADO COM PEND\xcaNCIA"),
                    (5, "VALIDADO SEM PEND\xcaNCIA"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="validation",
            name="state",
            field=models.IntegerField(
                default=5,
                blank=True,
                verbose_name="Estado",
                choices=[
                    (4, "VALIDADO COM PEND\xcaNCIA"),
                    (5, "VALIDADO SEM PEND\xcaNCIA"),
                ],
            ),
        ),
    ]
