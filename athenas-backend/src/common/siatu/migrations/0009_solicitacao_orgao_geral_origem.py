# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("siatu", "0008_auto_20160510_1151"),
    ]

    operations = [
        migrations.AddField(
            model_name="solicitacao",
            name="orgao_geral_origem",
            field=models.ForeignKey(
                related_name="orgao_origem",
                verbose_name="Origem",
                blank=True,
                to="rh.OrgaoGeral",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
