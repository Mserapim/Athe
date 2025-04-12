# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0042_auto_20170815_1555"),
    ]

    operations = [
        migrations.AddField(
            model_name="correctionfactor",
            name="ref_difference_cache",
            field=models.CharField(
                default="", max_length=6, verbose_name="Identificador", db_index=True
            ),
        ),
        migrations.AddField(
            model_name="correctionfactor",
            name="ref_payment_cache",
            field=models.CharField(
                default="", max_length=15, verbose_name="Identificador", db_index=True
            ),
        ),
        migrations.AlterField(
            model_name="genreevent",
            name="config_transparency",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name="Portal Transpar\xeancia",
                choices=[
                    (39, "VERBAS EXERCICIOS ANTERIORES"),
                    (1, "REMUNERA\xc7\xc3O: Subs\xeddio"),
                    (3, "REMUNERA\xc7\xc3O: Gratifica\xe7\xe3o de Representa\xe7\xe3o"),
                    (4, "REMUNERA\xc7\xc3O: VPI"),
                    (5, "REMUNERA\xc7\xc3O: Adicional de F\xe9rias"),
                    (6, "REMUNERA\xc7\xc3O: Abono Perman\xeancia"),
                    (7, "REMUNERA\xc7\xc3O: Gratifica\xe7\xe3o Natilina"),
                    (8, "RECIS\xd3RIA: F\xe9rias Vencidas"),
                    (9, "RECIS\xd3RIA: Adicional de F\xe9rias"),
                    (10, "RECIS\xd3RIA: Gratifica\xe7\xe3o Natalina"),
                    (11, "EFEITOS NEGATIVOS: Redutor de Teto"),
                    (12, "DEDU\xc7\xd4ES: IRRF"),
                    (13, "DEDU\xc7\xd4ES: IRRF - 13\xba Sal\xe1rio"),
                    (14, "DEDU\xc7\xd4ES: Previd\xeancia Social"),
                    (15, "DEDU\xc7\xd4ES: Previd\xeancia - 13\xba Sal\xe1rio"),
                    (16, "INDENIZAT\xd3RIAS: Aux. Alimenta\xe7\xe3o"),
                    (17, "INDENIZAT\xd3RIAS: Aux. Creche"),
                    (18, "INDENIZAT\xd3RIAS: Aux. Moradia"),
                    (19, "INDENIZAT\xd3RIAS: Aux. Transparte"),
                    (20, "INDENIZAT\xd3RIAS: Diferen\xe7a URV"),
                    (21, "INDENIZAT\xd3RIAS: Diferen\xe7a PAE"),
                    (22, "INDENIZAT\xd3RIAS: Abono de Perman\xeancia"),
                    (23, "INDENIZAT\xd3RIAS: Previd\xeancia Social"),
                    (24, "INDENIZAT\xd3RIAS: IRRF"),
                    (25, "Remunera\xe7\xe3o do Cargo Efetivo"),
                    (26, "Outras Verbas Remunerat\xf3rias, Legais ou Judiciais"),
                    (27, "Fun\xe7\xe3o de Confian\xe7a"),
                    (28, "Vencimento"),
                    (29, "Gratifica\xe7\xe3o"),
                    (30, "Gratifica\xe7\xe3o Natalina"),
                    (31, "F\xe9rias Constitucionais"),
                    (32, "Abono Perman\xeancia"),
                    (33, "Contribui\xe7\xe3o Previdenci\xe1ria"),
                    (34, "Imposto de Renda"),
                    (35, "Reten\xe7\xe3o por Teto Constitucional"),
                    (36, "Outros Redutores/Descontos"),
                    (37, "VERBAS INDENIZAT\xd3RIAS"),
                    (38, "OUTRAS REMUNERA\xc7\xd5ES RETROATIVAS/TEMPOR\xc1RIAS"),
                    (40, "OUTRAS REMUNERA\xc7\xd5ES TEMPOR\xc1RIAS"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="paycheckdifference",
            name="correction_factor_identifier",
            field=models.CharField(
                db_index=True,
                max_length=15,
                null=True,
                verbose_name="Fator de corre\xe7\xe3o",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="paycheckdifference",
            name="status",
            field=models.PositiveSmallIntegerField(
                default=1,
                verbose_name="Situa\xe7\xe3o",
                choices=[
                    (1, "ABERTO"),
                    (2, "PAGANDO PARCELADO"),
                    (3, "PARCIALMENTE PAGO"),
                    (4, "PAGO SEM INFORMA\xc7\xc3O"),
                    (5, "PAGO"),
                    (6, "IGNORADO"),
                    (7, "AGUARDANDO DECIS\xc3O"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="previdencia",
            name="identifier",
            field=models.PositiveSmallIntegerField(
                default=1, verbose_name="Identificador", choices=[(1, "1")]
            ),
        ),
    ]
