# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0016_auto_20181105_1852"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inspection",
            name="area_of_action",
            field=models.CharField(max_length=1000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="assignment",
            field=models.CharField(max_length=1000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="processesforanalysisperformanceinaudiences",
            name="audience_type",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Tipo de Audi\xeancia",
                blank=True,
                choices=[
                    (1, "N\xe3o informado"),
                    (2, "Concilia\xe7\xe3o"),
                    (3, "Instru\xe7\xe3o"),
                    (4, "Julgamento"),
                    (5, "Instru\xe7\xe3o e Julgamento"),
                    (6, "Preliminar"),
                    (7, "Interrogat\xf3rio"),
                    (8, "Inquiri\xe7\xe3o"),
                    (9, "Diploma\xe7\xe3o"),
                    (10, "Justifica\xe7\xe3o"),
                    (11, "Apresenta\xe7\xe3o"),
                    (12, "Apresenta\xe7\xe3o/Remiss\xe3o"),
                    (13, "Audi\xeancias gerais da Inf\xe2ncia e Juventude"),
                    (14, "Suspens\xe3o condicional do processo"),
                    (15, "Conciclia\xe7\xe3o, Instru\xe7\xe3o e Julgamento"),
                ],
            ),
        ),
    ]
