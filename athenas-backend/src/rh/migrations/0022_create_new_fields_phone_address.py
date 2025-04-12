# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0021_auto_20160512_1034"),
    ]

    operations = [
        migrations.AddField(
            model_name="endereco",
            name="general_organ",
            field=models.ForeignKey(
                related_name="address",
                verbose_name="Org\xe3o Geral",
                blank=True,
                to="rh.OrgaoGeral",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="endereco",
            name="person",
            field=models.ForeignKey(
                related_name="address",
                verbose_name="Pessoa",
                blank=True,
                to="rh.Pessoa",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="telefone",
            name="general_organ",
            field=models.ForeignKey(
                related_name="phone",
                verbose_name="Org\xe3o Geral",
                blank=True,
                to="rh.OrgaoGeral",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="telefone",
            name="person",
            field=models.ForeignKey(
                related_name="phone",
                verbose_name="Pessoa",
                blank=True,
                to="rh.Pessoa",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
