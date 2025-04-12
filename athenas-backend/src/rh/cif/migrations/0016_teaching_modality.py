# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cif", "0015_auto_20170926_1522"),
    ]

    operations = [
        migrations.AddField(
            model_name="teaching",
            name="modality",
            field=models.SmallIntegerField(
                default=0,
                null=True,
                verbose_name="Modalidade",
                blank=True,
                choices=[(1, "PRESENCIAL"), (2, "EAD")],
            ),
        ),
    ]
