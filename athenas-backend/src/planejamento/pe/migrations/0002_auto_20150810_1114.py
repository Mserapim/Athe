# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0001_initial"),
        ("pe", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="projeto",
            name="responsavel",
            field=models.ForeignKey(
                related_name="fkey_servidor_projeto",
                verbose_name="Respons\xe1vel",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="planejamento",
            name="objetivo",
            field=models.ManyToManyField(
                to="pe.Objetivo", null=True, verbose_name="Objetivo", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="objetivo",
            name="indicador",
            field=models.ManyToManyField(
                to="pe.Indicador", null=True, verbose_name="Indicador", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="objetivo",
            name="projeto",
            field=models.ManyToManyField(
                to="pe.Projeto", null=True, verbose_name="Projeto", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="indicadorvalor",
            name="indicador",
            field=models.ForeignKey(
                related_name="fkey_indicador_indicadorvalor",
                verbose_name="Indicador",
                to="pe.Indicador",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="indicador",
            name="indicadormeta",
            field=models.ManyToManyField(
                to="pe.IndicadorMeta",
                null=True,
                verbose_name="Indicador Meta",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="indicador",
            name="periodo",
            field=models.ForeignKey(
                related_name="fkey_periodo_indicador",
                verbose_name="Per\xedodo",
                to="pe.Periodo",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="andamentoprojeto",
            name="projeto",
            field=models.ForeignKey(
                related_name="fkey_projeto_andamentoprojeto",
                verbose_name="Projeto",
                to="pe.Projeto",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="analiseindicador",
            name="indicador",
            field=models.ForeignKey(
                related_name="fkey_analiseindicador_avaliacao",
                verbose_name="Indicador",
                to="pe.Indicador",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="analiseindicador",
            name="responsavel",
            field=models.ForeignKey(
                related_name="fkey_servidor_analiseindicador",
                verbose_name="Respons\xe1vel",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="analise",
            name="objetivo",
            field=models.ForeignKey(
                related_name="fkey_objetivo_avaliacao",
                verbose_name="Objetivo",
                to="pe.Objetivo",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="analise",
            name="responsavel",
            field=models.ForeignKey(
                related_name="fkey_servidor_analise",
                verbose_name="Respons\xe1vel",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
