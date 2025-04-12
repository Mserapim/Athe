# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0020_historicraf"),
    ]

    operations = [
        migrations.AddField(
            model_name="functionalactivityreport",
            name="close_date",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="functionalactivityreport",
            name="open_date",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="functionalactivityreport",
            name="process_date",
            field=models.DateTimeField(null=True, blank=True),
        ),
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
                ],
            ),
        ),
    ]
