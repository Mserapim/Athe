# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0029_auto_20160728_1356"),
    ]

    operations = [
        migrations.AddField(
            model_name="pessoafisica",
            name="sexual_orientation",
            field=models.PositiveSmallIntegerField(
                default=5,
                null=True,
                verbose_name="Orienta\xe7\xe3o Sexual",
                blank=True,
                choices=[
                    (1, "Heterossexual"),
                    (2, "Homossexual"),
                    (3, "Bissexual"),
                    (4, "Assexual"),
                    (5, "N\xe3o Informada"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="pessoafisica",
            name="social_name",
            field=models.CharField(
                max_length=100, null=True, verbose_name="Nome Social", blank=True
            ),
        ),
    ]
