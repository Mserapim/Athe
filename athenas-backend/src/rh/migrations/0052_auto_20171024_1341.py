# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0051_auto_20171017_1643"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="relationship",
            options={
                "verbose_name": "Rela\xe7\xe3o de Confian\xe7a",
                "permissions": (
                    (
                        "can_establish_any_trust_relationship",
                        "Pode estabelecer qualquer rela\xe7\xe3o de confian\xe7a",
                    ),
                ),
            },
        ),
        migrations.AlterField(
            model_name="dependente",
            name="pessoa_fisica",
            field=models.ForeignKey(
                related_name="dependentes_pessoa",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Pessoa F\xedsica",
                to="rh.PessoaFisica",
            ),
        ),
        migrations.AlterField(
            model_name="relationship",
            name="giver",
            field=models.ForeignKey(
                related_name="relationship_giver",
                verbose_name="Quem d\xe1",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
