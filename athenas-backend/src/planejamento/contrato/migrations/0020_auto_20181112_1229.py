# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0019_minutesolicitationrequisition"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contrato",
            name="tipo_contrato",
            field=models.IntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "Contrato"),
                    (2, "SRP"),
                    (3, "NE"),
                    (4, "Loca\xe7\xe3o"),
                    (5, "Servi\xe7os Cont\xednuos"),
                    (6, "Fornecimento"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="minuteitemaction",
            name="action",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Reativar"),
                    (2, "Desativar"),
                    (3, "Revogar"),
                    (4, "Aditivar"),
                ]
            ),
        ),
        migrations.AlterUniqueTogether(
            name="minutesolicitationcommitmentnote",
            unique_together=set([("number", "origin")]),
        ),
    ]
