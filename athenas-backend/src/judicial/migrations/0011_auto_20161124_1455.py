# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0010_auto_20161017_1204"),
    ]

    operations = [
        migrations.AddField(
            model_name="legalclassification",
            name="administrative_classification",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="legalclassification",
            name="disabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="legalclassification",
            name="glossary",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="type_vehicle",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Tipo de veiculo usado para a rezalizacao da diligencia",
                choices=[(1, "Ve\xedculo Oficial"), (2, "Ve\xedculo Particular")],
            ),
        ),
        migrations.AlterField(
            model_name="diligence",
            name="delivery_status",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="status da entrega",
                blank=True,
                choices=[
                    (1, "Redigindo a diligencia"),
                    (2, "Aguardando Distribu\xe7\xe3o"),
                    (3, "Aguardando Confirma\xe7\xe3o do Oficial"),
                    (4, "Entrega em andamento"),
                    (5, "Entrega Conclu\xedda"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="officerdiligence",
            name="status",
            field=models.SmallIntegerField(default=1, null=True),
        ),
    ]
