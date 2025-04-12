# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contabilidade", "0003_pparevisao_ativo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ppaacao",
            name="cache_codigo",
            field=models.CharField(max_length=40, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="ppaprograma",
            name="parent",
            field=models.ForeignKey(
                related_name="sub_programas",
                blank=True,
                to="contabilidade.PPAPrograma",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
