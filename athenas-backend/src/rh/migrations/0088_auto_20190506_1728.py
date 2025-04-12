# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0087_auto_20190502_1806"),
    ]

    operations = [
        migrations.AlterField(
            model_name="movimentacaorequisicao",
            name="category",
            field=models.IntegerField(
                default=301,
                verbose_name="Categoria eSocial origem",
                choices=[
                    (
                        305,
                        "Servidor indicado para conselho ou \xf3rg\xe3o deliberativo",
                    ),
                    (301, "Servidor P\xfablico Titular de Cargo Efetivo"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="servidor",
            name="categoria_cache",
            field=models.CharField(max_length=200),
        ),
    ]
