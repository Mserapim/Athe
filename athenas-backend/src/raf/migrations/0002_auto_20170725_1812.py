# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="subitem",
            name="productivy",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="activityadjustment",
            name="situation",
            field=models.PositiveSmallIntegerField(
                default=0,
                verbose_name="Situa\xe7\xe3o",
                choices=[
                    (0, "N\xe3o avaliado"),
                    (1, "Aguardando informa\xe7\xf5es"),
                    (2, "Deferido"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="subitemcalculate",
            name="affectation",
            field=models.PositiveSmallIntegerField(
                default=1,
                verbose_name="Afetar",
                choices=[(1, "Positivamente"), (2, "Negativamente")],
            ),
        ),
    ]
