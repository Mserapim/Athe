# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("processo", "0002_movimentacaoprocesso_processo_referencia_situacao"),
    ]

    operations = [
        migrations.AddField(
            model_name="processo",
            name="interessados",
            field=models.ManyToManyField(
                related_name="processo_interessado", to="rh.Pessoa"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="movimentacaoprocesso",
            name="historico_referencias",
            field=models.ManyToManyField(related_name="+", to="processo.Referencia"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="movimentacaoprocesso",
            name="situacao",
            field=models.ForeignKey(
                blank=True, to="processo.Situacao", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="justificativa",
            name="movimentacao",
            field=models.ForeignKey(
                related_name="justificativas",
                to="processo.MovimentacaoProcesso",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="justificativa",
            name="processo",
            field=models.ForeignKey(
                related_name="justificativas",
                to="processo.Processo",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="justificativa",
            name="usuario",
            field=models.ForeignKey(
                related_name="+", to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
