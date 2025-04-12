# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0007_auto_20180816_1304"),
    ]

    operations = [
        migrations.AlterField(
            model_name="promptnesscourtlawsuit",
            name="score_table",
            field=models.IntegerField(
                default=2,
                null=True,
                verbose_name="Tabela de C\xe1lculo",
                blank=True,
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
                    (14, "Cumula\xe7\xe3o de Atividades, Cargos e Fun\xe7\xf5es "),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="promptnessoutcourtlawsuit",
            name="score_table",
            field=models.IntegerField(
                default=2,
                null=True,
                verbose_name="Tabela de C\xe1lculo",
                blank=True,
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
                    (14, "Cumula\xe7\xe3o de Atividades, Cargos e Fun\xe7\xf5es "),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="promptnessuppermanagement",
            name="score_table",
            field=models.IntegerField(
                default=2,
                null=True,
                verbose_name="Tabela de C\xe1lculo",
                blank=True,
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
                    (14, "Cumula\xe7\xe3o de Atividades, Cargos e Fun\xe7\xf5es "),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="registeredpublicattendancenumber",
            name="score_table",
            field=models.IntegerField(
                default=1,
                null=True,
                verbose_name="Tabela de C\xe1lculo",
                blank=True,
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
                    (14, "Cumula\xe7\xe3o de Atividades, Cargos e Fun\xe7\xf5es "),
                ],
            ),
        ),
    ]
