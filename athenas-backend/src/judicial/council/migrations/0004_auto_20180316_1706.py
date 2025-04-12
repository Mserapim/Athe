# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("council", "0003_auto_20170905_1614"),
    ]

    operations = [
        migrations.AddField(
            model_name="colegialdecision",
            name="resume",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="rapporteurdocument",
            name="rapporteur_vote_type",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "A favor do pedido"),
                    (2, "Contra o pedido"),
                    (3, "Parcialmente favor\xe1vel"),
                    (201, "Declarar Impedimento"),
                    (202, "Declarar Suspei\xe7\xe3o"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="vote",
            name="vote_type",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "Acompanha o relator"),
                    (2, "N\xe3o acompanha o relator"),
                    (3, "Absten\xe7\xe3o"),
                    (4, "Homologado parcialmente"),
                ],
            ),
        ),
    ]
