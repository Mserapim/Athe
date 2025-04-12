# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0024_auto_20180430_1658"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicraf",
            name="action",
            field=models.PositiveSmallIntegerField(
                default=1,
                verbose_name="A\xe7\xe3o",
                choices=[
                    (1, "Inser\xe7\xe3o"),
                    (2, "Abertura"),
                    (3, "Fechamento"),
                    (4, "Submiss\xe3o"),
                    (5, "Submiss\xe3o / Membro afastado"),
                ],
            ),
        ),
    ]
