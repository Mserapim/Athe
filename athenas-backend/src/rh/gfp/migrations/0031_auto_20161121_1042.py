# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0030_referencianiveis2d_estrutura_salarial"),
    ]

    operations = [
        migrations.AddField(
            model_name="folhaevento",
            name="correct_qnt_max",
            field=models.DecimalField(
                default=0, max_digits=10, decimal_places=6, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="classification",
            field=models.PositiveIntegerField(
                default=1,
                verbose_name="Classifica\xe7\xe3o",
                choices=[(1, "Classifica\xe7\xe3o")],
            ),
        ),
    ]
