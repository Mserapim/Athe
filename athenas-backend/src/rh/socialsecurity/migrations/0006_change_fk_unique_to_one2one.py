# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("socialsecurity", "0005_contribution_and_integral_prevision_dates_null"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employmentbond",
            name="possession",
            field=models.OneToOneField(
                null=True,
                verbose_name="Movimenta\xe7\xe3o de Posse",
                to="rh.MovimentacaoPosse",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="retirementprevision",
            name="natural_person",
            field=models.OneToOneField(
                verbose_name="Pessoa f\xedsica",
                to="rh.PessoaFisica",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
