# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0001_initial"),
        ("mto", "0001_initial"),
        ("contabilidade", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="pparevisao",
            name="publicacao",
            field=models.ForeignKey(
                related_name="revisoes_ppa",
                to="rh.Publicacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="ppaprograma",
            name="parent",
            field=models.ForeignKey(
                related_name="sub_programas",
                to="contabilidade.PPAPrograma",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="ppaprograma",
            name="revisao",
            field=models.ForeignKey(
                related_name="programas",
                to="contabilidade.PPARevisao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="ppaacao",
            name="fonte_exclusiva",
            field=models.ForeignKey(
                related_name="acoes_vinculadas",
                to="contabilidade.FonteRecurso",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="ppaacao",
            name="programa",
            field=models.ForeignKey(
                related_name="acoes",
                to="contabilidade.PPAPrograma",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="categoria",
            name="elemento_despesa_subitem",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                to="mto.ElementoDespesaSubItem", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="categoria",
            name="grupo_contabil",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                to="contabilidade.GrupoContabil", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="categoria",
            unique_together=set([("elemento_despesa_subitem", "grupo_contabil")]),
        ),
    ]
