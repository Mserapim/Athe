# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apd", "0005_auto_20171201_1122"),
    ]

    operations = [
        migrations.AddField(
            model_name="periodicevaluationperformance",
            name="copied_from_stage",
            field=models.BooleanField(
                default=False, verbose_name="Copiado do est\xc3\xa1gio?"
            ),
        ),
        migrations.AddField(
            model_name="periodicevaluationperformance",
            name="final_score",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=11,
                blank=True,
                null=True,
                verbose_name="M\xe9dia final",
            ),
        ),
        migrations.AddField(
            model_name="periodicevaluationperformance",
            name="top_score",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=11,
                blank=True,
                null=True,
                verbose_name="M\xe9dia m\xe1xima",
            ),
        ),
    ]
