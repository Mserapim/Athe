# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0082_auto_20190405_1623"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lotacao",
            name="allow_lawsuit",
            field=models.BooleanField(
                default=False, verbose_name="Habilita para Procedimentos Extrajudiciais"
            ),
        ),
        migrations.AlterField(
            model_name="socialsecurityconfig",
            name="mass_segregation_plan",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "Plano previdenci\xe1rio ou \xfanico"),
                    (2, "Plano financeiro"),
                ],
            ),
        ),
    ]
