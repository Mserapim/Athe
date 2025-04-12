# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0072_auto_20181211_1400"),
        ("registration", "0005_auto_20180509_1700"),
    ]

    operations = [
        migrations.AddField(
            model_name="forminformation",
            name="address_country",
            field=models.ForeignKey(
                related_name="forminformation_address_country",
                verbose_name="Pa\xeds(Residentes no Exterior)",
                blank=True,
                to="rh.Pais",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="forminformation",
            name="address_country_diff",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="forminformation",
            name="address_outsider",
            field=models.BooleanField(
                default=False, verbose_name="Endere\xe7o no exterior"
            ),
        ),
        migrations.AddField(
            model_name="forminformation",
            name="address_outsider_citty",
            field=models.CharField(
                max_length=50, null=True, verbose_name="Cidade no Exterior", blank=True
            ),
        ),
        migrations.AddField(
            model_name="forminformation",
            name="address_outsider_citty_diff",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="forminformation",
            name="address_outsider_diff",
            field=models.BooleanField(default=False),
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
                    (51, "CERTID\xc3O DE CASAMENTO"),
                    (52, "COMPROVANTE DE ENDERE\xc7O"),
                    (53, "TERMO DE CUSTODIA DE MENOR"),
                    (54, "UNIAO ESTAVEL"),
                ],
            ),
        ),
    ]
