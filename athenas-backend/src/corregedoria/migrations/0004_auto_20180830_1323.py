# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("corregedoria", "0003_auto_20180530_1505"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bandscoretable",
            name="end_value",
            field=models.DecimalField(
                null=True, max_digits=16, decimal_places=2, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="bandscoretable",
            name="initial_value",
            field=models.DecimalField(
                null=True, max_digits=16, decimal_places=2, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="configproductivity",
            name="score_table",
            field=models.IntegerField(
                verbose_name="Tabela de C\xe1lculo",
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
                    (14, "Cumula\xe7\xe3o de atividades, cargos e fun\xe7\xf5es"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="configscoretable",
            name="score_table",
            field=models.IntegerField(
                verbose_name="Tabela de C\xe1lculo",
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
                    (14, "Cumula\xe7\xe3o de atividades, cargos e fun\xe7\xf5es"),
                ],
            ),
        ),
    ]
