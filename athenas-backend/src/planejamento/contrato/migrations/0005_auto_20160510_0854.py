# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0004_outsourced"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contrato",
            name="responsaveis",
            field=models.ManyToManyField(
                related_name="contratos_indiretos", to="contrato.Gestor"
            ),
        ),
        migrations.AlterField(
            model_name="gestor",
            name="user",
            field=models.OneToOneField(
                related_name="como_gestor",
                verbose_name="Usu\xe1rio",
                to=settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
