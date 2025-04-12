# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("patrimonio", "0008_auto_20170510_1541"),
    ]

    operations = [
        migrations.AddField(
            model_name="especie",
            name="status",
            field=models.SmallIntegerField(
                default=1, db_index=True, choices=[(1, "Ativo"), (2, "Inativo")]
            ),
        ),
        migrations.AlterField(
            model_name="patrimonio",
            name="data_baixa",
            field=models.DateField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="patrimonio",
            name="localizacao",
            field=models.ForeignKey(
                related_name="patrimonios",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="patrimonio.Localizacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="patrimonio",
            name="responsavel",
            field=models.ForeignKey(
                related_name="patrimonios",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Servidor",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="patrimonio",
            name="suspenso_tipo",
            field=models.SmallIntegerField(
                default=1,
                choices=[
                    (1, "Suspens\xe3o de Nota de Entrada"),
                    (2, "Suspens\xe3o de Item de Entrada"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="patrimonio",
            name="utilizado_por",
            field=models.ForeignKey(
                related_name="utilizando_patrimonios",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Servidor",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="patrimonio",
            name="vida_util",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="patrimoniohistorico",
            name="suspenso_tipo",
            field=models.SmallIntegerField(
                default=1,
                choices=[
                    (1, "Suspens\xe3o de Nota de Entrada"),
                    (2, "Suspens\xe3o de Item de Entrada"),
                ],
            ),
        ),
    ]
