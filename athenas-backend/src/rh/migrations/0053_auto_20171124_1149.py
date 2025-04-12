# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0052_auto_20171024_1341"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pessoafisica",
            name="sexual_orientation",
            field=models.PositiveSmallIntegerField(
                default=5,
                verbose_name="Orienta\xe7\xe3o Sexual",
                choices=[
                    (1, "HETEROSSEXUAL"),
                    (2, "HOMOSSEXUAL"),
                    (3, "BISSEXUAL"),
                    (4, "ASSEXUAL"),
                    (5, "N\xc3O INFORMADA"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="relationship",
            name="app",
            field=models.IntegerField(
                default=1, verbose_name="Aplicativo", choices=[(1, "diarias")]
            ),
        ),
    ]
