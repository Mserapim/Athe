# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0077_socialsecurityconfig"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="encargofinanceiro",
            options={"ordering": ["data_inicio"], "verbose_name": "Encargo Financeiro"},
        ),
        migrations.AlterModelOptions(
            name="periodorequisicao",
            options={
                "ordering": ["data_inicio"],
                "verbose_name": "Per\xedodo de requisi\xe7\xe3o",
            },
        ),
        migrations.AddField(
            model_name="unidadeadministrativa",
            name="cnae_preponderant",
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
    ]
