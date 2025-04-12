# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0083_auto_20190408_1546"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dependente",
            name="responsavel",
            field=models.ForeignKey(
                related_name="responsavel_dependentes",
                verbose_name="Respons\xe1vel",
                blank=True,
                to="rh.PessoaFisica",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
