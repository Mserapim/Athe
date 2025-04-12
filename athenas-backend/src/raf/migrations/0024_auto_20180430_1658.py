# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("afastamento", "0006_auto_20180207_1659"),
        ("raf", "0023_auto_20180403_1728"),
    ]

    operations = [
        migrations.AddField(
            model_name="functionalactivityreport",
            name="departure",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="functionalactivityreport",
            name="departures",
            field=models.ManyToManyField(
                related_name="_functionalactivityreport_departures_+",
                to="afastamento.BaseLicencaAfastamento",
            ),
        ),
        migrations.AlterField(
            model_name="subitem",
            name="productivity",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Produtividade",
                choices=[
                    (1, "N\xe3o se aplica"),
                    (2, "Presteza  - Feitos Judiciais"),
                    (3, "Presteza  - Feitos Extrajudiciais"),
                    (4, "Presteza  - Atendimento tempestivo \xe0s determina\xe7\xf5es"),
                    (5, "Produtividade - Fator I - Pe\xe7as Iniciais"),
                    (6, "Produtividade - Fator I - Procedimentos Administrativos"),
                    (7, "Produtividade - Fator II - Pe\xe7as Judiciais"),
                    (8, "Produtividade - Fator II - Procedimentos Administrativos"),
                    (9, "Produtividade - Fator III"),
                    (10, "Produtividade - Fator IV - Audi\xeancias Judiciais"),
                    (
                        11,
                        "Produtividade - Fator IV - Aud. P\xfablicas ou Administrativas",
                    ),
                    (12, "Produtividade - Fator IV - J\xfaris"),
                    (13, "Atendimento ao P\xfablico"),
                ],
            ),
        ),
    ]
