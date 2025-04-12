# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from planejamento.contrato.models import ValorContrato, Contrato


def ordem_refactory(apps, schema_editor):
    ValorContrato.objects.filter(ordem=100).update(ordem=1)

    for c in Contrato.objects.filter():
        seq = 0
        for v in ValorContrato.objects.filter(contrato__pk=c.pk).order_by(
            "data_ref_inicio"
        ):
            seq = seq + 1
            ValorContrato.objects.filter(pk=v.pk).update(ordem=seq)


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0009_auto_20170517_1633"),
    ]

    operations = [
        migrations.AlterField(
            model_name="valorcontrato",
            name="ordem",
            field=models.IntegerField(
                default=1,
                null=True,
                blank=True,
                choices=[
                    (1, "Principal"),
                    (2, "1\xb0 Aditivo"),
                    (3, "2\xb0 Aditivo"),
                    (4, "3\xb0 Aditivo"),
                    (5, "4\xb0 Aditivo"),
                    (6, "5\xb0 Aditivo"),
                    (7, "6\xb0 Aditivo"),
                    (8, "7\xb0 Aditivo"),
                    (9, "8\xb0 Aditivo"),
                    (10, "9\xb0 Aditivo"),
                    (11, "10\xb0 Aditivo"),
                    (12, "11\xb0 Aditivo"),
                    (13, "12\xb0 Aditivo"),
                    (14, "13\xb0 Aditivo"),
                    (15, "14\xb0 Aditivo"),
                    (16, "15\xb0 Aditivo"),
                    (17, "16\xb0 Aditivo"),
                    (18, "17\xb0 Aditivo"),
                    (19, "18\xb0 Aditivo"),
                    (20, "19\xb0 Aditivo"),
                    (21, "20\xb0 Aditivo"),
                    (22, "21\xb0 Aditivo"),
                    (23, "22\xb0 Aditivo"),
                    (24, "23\xb0 Aditivo"),
                    (25, "24\xb0 Aditivo"),
                    (26, "25\xb0 Aditivo"),
                ],
            ),
        ),
        migrations.RunPython(ordem_refactory),
    ]


# os que tem 1, vira principaç  os que são 100, vira principal  ordenar...
