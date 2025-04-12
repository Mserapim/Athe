# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pe", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.AlterField(
            model_name="indicador",
            name="indicadormeta",
            field=models.ManyToManyField(
                to="pe.IndicadorMeta", verbose_name="Indicador Meta"
            ),
        ),
        migrations.AlterField(
            model_name="objetivo",
            name="indicador",
            field=models.ManyToManyField(to="pe.Indicador", verbose_name="Indicador"),
        ),
        migrations.AlterField(
            model_name="objetivo",
            name="projeto",
            field=models.ManyToManyField(to="pe.Projeto", verbose_name="Projeto"),
        ),
        migrations.AlterField(
            model_name="planejamento",
            name="objetivo",
            field=models.ManyToManyField(to="pe.Objetivo", verbose_name="Objetivo"),
        ),
    ]
