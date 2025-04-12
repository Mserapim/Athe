# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0086_orgaogeral_cache_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="movimentacaorequisicao",
            name="category",
            field=models.IntegerField(
                default=301,
                verbose_name="Categoria eSocial origem",
                choices=[
                    (301, "Servidor P\xfablico Titular de Cargo Efetivo"),
                    (
                        305,
                        "Servidor indicado para conselho ou \xf3rg\xe3o deliberativo",
                    ),
                ],
            ),
        ),
    ]
