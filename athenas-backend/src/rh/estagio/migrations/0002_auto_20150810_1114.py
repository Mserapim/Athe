# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("estagio", "0001_initial"),
        ("questionario", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="quesitoavaliacao",
            name="elemento",
            field=models.ManyToManyField(
                related_name="quesito_avaliacao", to="questionario.Elemento"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="quesitoavaliacao",
            name="fator_avaliacao",
            field=models.ForeignKey(
                related_name="quesito_avaliacao",
                to="estagio.FatorAvaliacao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="manifestacaoestagio",
            name="estagio_avaliacao",
            field=models.ForeignKey(
                related_name="manifestacao_servidor",
                to="estagio.EstagioAvaliacao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="manifestacaoestagio",
            name="questionario_resposta",
            field=models.ForeignKey(
                related_name="manifestacao_servidor",
                to="questionario.QuestionarioResposta",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="manifestacaoestagio",
            name="servidor",
            field=models.ForeignKey(
                related_name="manifestacao_servidor",
                to="estagio.EstagioProbatorioServidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="integrantescomissao",
            name="comissao_id",
            field=models.ForeignKey(
                to="estagio.ComissaoAvaliadora", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="integrantescomissao",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="integrantescomissao",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=True,
        ),
    ]
