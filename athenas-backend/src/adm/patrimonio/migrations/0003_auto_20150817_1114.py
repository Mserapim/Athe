# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("patrimonio", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.RenameField(
            model_name="patrimoniohistorico",
            old_name="autor",
            new_name="who",
        ),
        migrations.AddField(
            model_name="patrimonio",
            name="suspenso_tipo",
            field=models.SmallIntegerField(
                default=1,
                choices=[
                    (1, "Suspens\xe3o de Nota de Entrada"),
                    (2, "Suspens\xe3o de Item de Entrada"),
                ],
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="patrimoniohistorico",
            name="suspenso_tipo",
            field=models.SmallIntegerField(
                default=1,
                choices=[
                    (1, "Suspens\xe3o de Nota de Entrada"),
                    (2, "Suspens\xe3o de Item de Entrada"),
                ],
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="patrimoniohistorico",
            name="when",
            field=models.DateTimeField(
                default=datetime.datetime(1900, 1, 1, 0, 0, 1), auto_now_add=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="suspensao",
            name="item_entrada",
            field=models.ForeignKey(
                related_name="suspensoes",
                on_delete=django.db.models.deletion.PROTECT,
                to="patrimonio.ItemEntrada",
                null=True,
            ),
            preserve_default=True,
        ),
    ]
