# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0002_datamigration_start"),
    ]

    operations = [
        migrations.AlterField(
            model_name="forminformation",
            name="professional_council_issuer",
            field=models.CharField(
                default="",
                max_length=256,
                null=True,
                verbose_name="Conselho Profissional - Org\xe3o de Expedi\xe7\xe3o",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="forminformation",
            name="ric_issuer",
            field=models.CharField(
                default="",
                max_length=256,
                null=True,
                verbose_name="RIC - Org\xe3o Emissor",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="forminformation",
            name="rne_issuer",
            field=models.CharField(
                default="",
                max_length=256,
                null=True,
                verbose_name="RNE - Org\xe3o Emissor",
                blank=True,
            ),
        ),
    ]
