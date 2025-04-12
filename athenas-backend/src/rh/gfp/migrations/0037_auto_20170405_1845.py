# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0036_auto_20170330_1135"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="referencianiveis2d",
            options={"ordering": ("estrutura_salarial", "ordem")},
        ),
        migrations.AlterField(
            model_name="movimentacaoprogressao",
            name="progressao_anterior",
            field=models.ForeignKey(
                related_name="progressoes",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="gfp.MovimentacaoProgressao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="movimentacaoprogressao",
            name="referencia_nivel2d",
            field=models.ForeignKey(
                related_name="referencia_progressoes",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Refer\xeancia N\xedveis",
                blank=True,
                to="gfp.ReferenciaNiveis2D",
            ),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="modelo_tabela",
            field=models.ForeignKey(
                related_name="referencias",
                verbose_name="Modelo",
                blank=True,
                to="gfp.ModeloTabelaSalarial",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterUniqueTogether(
            name="referencianiveis2d",
            unique_together=set([("estrutura_salarial", "horizontal", "vertical")]),
        ),
    ]
