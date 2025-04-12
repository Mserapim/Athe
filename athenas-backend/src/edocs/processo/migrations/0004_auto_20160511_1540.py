# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("processo", "0003_auto_20150810_1114"),
    ]

    operations = [
        migrations.AlterField(
            model_name="justificativa",
            name="justificativa",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="justificativa",
            name="valor_antigo",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="justificativa",
            name="valor_novo",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="movimentacaoprocesso",
            name="volume",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="processo",
            name="ano",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="processo",
            name="assunto_processo",
            field=models.ForeignKey(
                to="processo.Assunto", blank=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="processo",
            name="caixa",
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="processo",
            name="codigo_processo",
            field=models.CharField(unique=True, max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name="processo",
            name="motivo_excluido",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="processo",
            name="numero",
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="processo",
            name="paginas",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="processo",
            name="volume",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
    ]
