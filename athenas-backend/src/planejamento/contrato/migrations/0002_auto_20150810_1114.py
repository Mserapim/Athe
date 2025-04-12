# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contrato", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="notaempenho",
            name="fornecedor",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Pessoa",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="notaempenho",
            name="ne_anterior",
            field=models.ForeignKey(
                related_name="ne_principal",
                blank=True,
                to="contrato.NotaEmpenho",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="notaempenho",
            name="ref_valor_contrato",
            field=models.ForeignKey(
                related_name="ne_ref_valor_contrato",
                to="contrato.ValorContrato",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="medicao",
            name="contrato",
            field=models.ForeignKey(
                related_name="medicoes",
                to="contrato.Contrato",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="medicao",
            name="nota_empenho",
            field=models.ForeignKey(
                related_name="medicoes",
                to="contrato.NotaEmpenho",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="medicao",
            name="user",
            field=models.ForeignKey(
                related_name="minhas_medicoes",
                to=settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="gestor",
            name="user",
            field=models.ForeignKey(
                related_name="como_gestor",
                verbose_name="Usu\xe1rio",
                to=settings.AUTH_USER_MODEL,
                unique=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="envionefornecedor",
            name="criado_por",
            field=models.ForeignKey(
                related_name="+", to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="envionefornecedor",
            name="nota_empenho",
            field=models.ForeignKey(
                related_name="envio_ne_fornecedor",
                to="contrato.NotaEmpenho",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contrato",
            name="gestor",
            field=models.ForeignKey(
                related_name="contratos", to="contrato.Gestor", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contrato",
            name="pessoa",
            field=models.ManyToManyField(related_name="contratos", to="rh.Pessoa"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contrato",
            name="responsaveis",
            field=models.ManyToManyField(
                related_name="contratos_indiretos",
                null=True,
                to="contrato.Gestor",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="adtivo",
            name="contrato",
            field=models.ForeignKey(
                related_name="adtivos", to="contrato.Contrato", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="adtivo",
            name="user",
            field=models.ForeignKey(
                related_name="meus_adtivos",
                to=settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="acaocontrato",
            name="contrato",
            field=models.ForeignKey(
                related_name="acoes", to="contrato.Contrato", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="acaocontrato",
            name="user",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
