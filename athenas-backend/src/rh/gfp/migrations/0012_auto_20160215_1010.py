# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0011_auto_20160211_1106"),
    ]

    operations = [
        migrations.AlterField(
            model_name="evento",
            name="config_transparencia",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name="Portal Transpar\xeancia",
                choices=[
                    (3101, "DEDU\xc7\xd4ES: IRRF"),
                    (3102, "DEDU\xc7\xd4ES: IRRF - 13\xba Sal\xe1rio"),
                    (3103, "DEDU\xc7\xd4ES: Previd\xeancia Social"),
                    (3104, "DEDU\xc7\xd4ES: Previd\xeancia - 13\xba Sal\xe1rio"),
                    (4001, "INDENIZAT\xd3RIAS: Aux. Alimenta\xe7\xe3o"),
                    (4002, "INDENIZAT\xd3RIAS: Aux. Creche"),
                    (4003, "INDENIZAT\xd3RIAS: Aux. Transparte"),
                    (4004, "INDENIZAT\xd3RIAS: Diferen\xe7a URV"),
                    (4005, "INDENIZAT\xd3RIAS: Diferen\xe7a PAE"),
                    (4006, "INDENIZAT\xd3RIAS: Abono de Perman\xeancia"),
                    (4007, "INDENIZAT\xd3RIAS: Previd\xeancia Social"),
                    (4008, "INDENIZAT\xd3RIAS: IRRF"),
                    (4009, "INDENIZAT\xd3RIAS: Aux. Moradia"),
                    (3001, "EFEITOS NEGATIVOS: Redutor de Teto"),
                    (2001, "RECIS\xd3RIA: F\xe9rias Vencidas"),
                    (2002, "RECIS\xd3RIA: Adicional de F\xe9rias"),
                    (2003, "RECIS\xd3RIA: Gratifica\xe7\xe3o Natalina"),
                    (1001, "REMUNERA\xc7\xc3O: Subs\xeddio"),
                    (1002, "REMUNERA\xc7\xc3O: Vencimento"),
                    (
                        1003,
                        "REMUNERA\xc7\xc3O: Gratifica\xe7\xe3o de Representa\xe7\xe3o",
                    ),
                    (1004, "REMUNERA\xc7\xc3O: VPI"),
                    (1005, "REMUNERA\xc7\xc3O: Adicional de F\xe9rias"),
                    (1006, "REMUNERA\xc7\xc3O: Abono Perman\xeancia"),
                    (1007, "REMUNERA\xc7\xc3O: Gratifica\xe7\xe3o Natilina"),
                ],
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="folhatipo",
            name="numero",
            field=models.CharField(unique=True, max_length=4, verbose_name="N\xfamero"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="genreevent",
            name="config_transparency",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name="Portal Transpar\xeancia",
                choices=[
                    (3101, "DEDU\xc7\xd4ES: IRRF"),
                    (3102, "DEDU\xc7\xd4ES: IRRF - 13\xba Sal\xe1rio"),
                    (3103, "DEDU\xc7\xd4ES: Previd\xeancia Social"),
                    (3104, "DEDU\xc7\xd4ES: Previd\xeancia - 13\xba Sal\xe1rio"),
                    (4001, "INDENIZAT\xd3RIAS: Aux. Alimenta\xe7\xe3o"),
                    (4002, "INDENIZAT\xd3RIAS: Aux. Creche"),
                    (4003, "INDENIZAT\xd3RIAS: Aux. Transparte"),
                    (4004, "INDENIZAT\xd3RIAS: Diferen\xe7a URV"),
                    (4005, "INDENIZAT\xd3RIAS: Diferen\xe7a PAE"),
                    (4006, "INDENIZAT\xd3RIAS: Abono de Perman\xeancia"),
                    (4007, "INDENIZAT\xd3RIAS: Previd\xeancia Social"),
                    (4008, "INDENIZAT\xd3RIAS: IRRF"),
                    (4009, "INDENIZAT\xd3RIAS: Aux. Moradia"),
                    (3001, "EFEITOS NEGATIVOS: Redutor de Teto"),
                    (2001, "RECIS\xd3RIA: F\xe9rias Vencidas"),
                    (2002, "RECIS\xd3RIA: Adicional de F\xe9rias"),
                    (2003, "RECIS\xd3RIA: Gratifica\xe7\xe3o Natalina"),
                    (1001, "REMUNERA\xc7\xc3O: Subs\xeddio"),
                    (1002, "REMUNERA\xc7\xc3O: Vencimento"),
                    (
                        1003,
                        "REMUNERA\xc7\xc3O: Gratifica\xe7\xe3o de Representa\xe7\xe3o",
                    ),
                    (1004, "REMUNERA\xc7\xc3O: VPI"),
                    (1005, "REMUNERA\xc7\xc3O: Adicional de F\xe9rias"),
                    (1006, "REMUNERA\xc7\xc3O: Abono Perman\xeancia"),
                    (1007, "REMUNERA\xc7\xc3O: Gratifica\xe7\xe3o Natilina"),
                ],
            ),
            preserve_default=True,
        ),
    ]
