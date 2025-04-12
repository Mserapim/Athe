# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0061_auto_20180228_1539"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cargo",
            name="requires_profissional_council",
        ),
        migrations.AddField(
            model_name="quadro",
            name="requires_profissional_council",
            field=models.BooleanField(
                default=False, verbose_name="Exige Conselho Profissional"
            ),
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
                    (51, "CERTID\xc3O DE CASAMENTO"),
                    (52, "COMPROVANTE DE ENDERE\xc7O"),
                    (53, "TERMO DE CUSTODIA DE MENOR"),
                    (54, "TERMO DE UNIAO ESTAVEL"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="docsdadosespecificos",
            name="especificidade",
            field=models.IntegerField(
                verbose_name="Especificidade",
                choices=[
                    (1, "T\xcdTULO DE ELEITOR.ZONA"),
                    (2, "T\xcdTULO DE ELEITOR.SE\xc7\xc3O"),
                    (3, "T\xcdTULO DE ELEITOR.UF"),
                    (4, "CNH.CATEGORIA"),
                    (5, "RESERVISTA.CLASSE"),
                    (6, "CTPS.S\xc9RIE"),
                    (7, "T\xcdTULO DE ELEITOR.MUNICIPIO"),
                    (8, "CTPS.UF"),
                    (9, "RIC.EMISSOR"),
                    (10, "RNE.EMISSOR"),
                    (11, "CONSELHO PROFISSIONAL.EMISSOR"),
                    (12, "CNH.DATA PRIMEIRA HABILITA\xc7\xc3O"),
                    (13, "RG.EMISSOR"),
                ],
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
                ],
            ),
        ),
        migrations.AlterField(
            model_name="telefone",
            name="description",
            field=models.CharField(
                default="", max_length=80, verbose_name="Descri\xe7\xe3o", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="telefone",
            name="tipo_telefone",
            field=models.IntegerField(
                verbose_name="Tipo de Telefone",
                choices=[
                    (1, "RESIDENCIAL"),
                    (2, "COMERCIAL"),
                    (3, "CELULAR"),
                    (4, "FAX"),
                    (5, "INSTITUCIONAL"),
                    (6, "CONTATO EMERG\xcaNCIA"),
                ],
            ),
        ),
    ]
