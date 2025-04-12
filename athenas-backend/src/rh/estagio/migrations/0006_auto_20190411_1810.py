# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("estagio", "0005_auto_20160510_1148"),
    ]

    operations = [
        migrations.AlterField(
            model_name="decisaochefeorgao",
            name="decisao",
            field=models.CharField(
                default=2,
                max_length=1,
                blank=True,
                choices=[(1, "HOMOLOGA"), (2, "N\xc3O HOMOLOGA")],
            ),
        ),
        migrations.AlterField(
            model_name="integrantescomissao",
            name="tipo_participante",
            field=models.CharField(
                default=4,
                max_length=1,
                choices=[
                    ("1", "PRESIDENTE"),
                    ("3", "INTEGRANTE"),
                    ("2", "SECRET\xc1RIO"),
                    ("4", "SUPLENTE"),
                ],
            ),
        ),
    ]
