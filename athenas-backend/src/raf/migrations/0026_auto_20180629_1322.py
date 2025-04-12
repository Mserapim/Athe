# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0025_auto_20180519_0246"),
    ]

    operations = [
        migrations.AddField(
            model_name="typequiz",
            name="group",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Grupo",
                choices=[
                    (1, "Judicial"),
                    (2, "Extrajudicial"),
                    (3, "N\xe3o-procedimentais"),
                    (4, "Militar judicial"),
                    (5, "Militar extrajudicial"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="typequiz",
            name="species",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Esp\xe9cie",
                choices=[
                    (1, "C\xedvel"),
                    (2, "Criminal"),
                    (3, "Inf\xe2ncia e Juventude"),
                    (4, "Eleitoral"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="historicraf",
            name="action",
            field=models.PositiveSmallIntegerField(
                default=1,
                verbose_name="A\xe7\xe3o",
                choices=[
                    (1, "Inser\xe7\xe3o"),
                    (2, "Abertura"),
                    (3, "Fechamento"),
                    (4, "Submiss\xe3o"),
                    (5, "Submiss\xe3o / Membro afastado"),
                    (6, "Tentativa Submiss\xe3o - RAF Fechado"),
                    (7, "Tentativa Submiss\xe3o - RAF j\xe1 submetido"),
                    (8, "Tentativa Submiss\xe3o - Sem permiss\xe3o de submiss\xe3o"),
                    (9, "Tentativa Submiss\xe3o - RAF Anterior N\xc3O SUBMETIDO"),
                ],
            ),
        ),
    ]
