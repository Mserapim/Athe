# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pensao", "0001_initial"),
        ("rh", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="pensao",
            name="pensionista",
            field=models.ForeignKey(
                related_name="pensao_pensionista",
                verbose_name="Pensionista",
                to="rh.PessoaFisica",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pensao",
            name="publicacao",
            field=models.ForeignKey(
                related_name="pensao_publicacao",
                verbose_name="Publica\xe7\xe3o",
                blank=True,
                to="rh.Publicacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pensao",
            name="representante_legal",
            field=models.ForeignKey(
                related_name="pensao_representante_legal",
                to="rh.PessoaFisica",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pensao",
            name="servidor",
            field=models.ForeignKey(
                related_name="pensao_pagador",
                verbose_name="Servidor",
                to="rh.Servidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
