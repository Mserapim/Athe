# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0006_auto_20150921_1434"),
        ("siatu", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="avaliacao",
            name="avaliacao_neutra",
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="avaliacao",
            name="justificativa_netra",
            field=models.TextField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="avaliacao",
            name="neutralizado_por",
            field=models.ForeignKey(
                related_name="+", to="rh.Servidor", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="esclarecimento",
            field=models.SmallIntegerField(
                default=0,
                choices=[
                    (1, "P\xe9ssimo"),
                    (2, "Ruim"),
                    (3, "Regular"),
                    (4, "Bom"),
                    (5, "\xd3timo"),
                    (6, "N\xe3o avaliado"),
                ],
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="presteza",
            field=models.SmallIntegerField(
                default=0,
                choices=[
                    (1, "P\xe9ssimo"),
                    (2, "Ruim"),
                    (3, "Regular"),
                    (4, "Bom"),
                    (5, "\xd3timo"),
                    (6, "N\xe3o avaliado"),
                ],
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="satisfacao",
            field=models.SmallIntegerField(
                choices=[
                    (1, "P\xe9ssimo"),
                    (2, "Ruim"),
                    (3, "Regular"),
                    (4, "Bom"),
                    (5, "\xd3timo"),
                    (6, "N\xe3o avaliado"),
                ]
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="tempo",
            field=models.SmallIntegerField(
                default=0,
                choices=[
                    (1, "P\xe9ssimo"),
                    (2, "Ruim"),
                    (3, "Regular"),
                    (4, "Bom"),
                    (5, "\xd3timo"),
                    (6, "N\xe3o avaliado"),
                ],
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="status",
            name="status",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Aberto"),
                    (2, "Aguardando atendimento"),
                    (3, "Em atendimento"),
                    (4, "Aguardando avalia\xe7\xe3o"),
                    (5, "Transferido para outro atendente"),
                    (6, "Terceirizada"),
                    (7, "Garantia"),
                    (8, "Em Viagem"),
                    (9, "Conclu\xeddo"),
                    (10, "Aguardando entrega"),
                    (11, "Em manuten\xe7\xe3o"),
                    (12, "N\xe3o Avaliado"),
                ]
            ),
            preserve_default=True,
        ),
    ]
