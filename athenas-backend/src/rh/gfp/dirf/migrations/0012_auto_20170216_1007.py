# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ged", "0003_auto_20151014_1609"),
        ("dirf", "0011_auto_20170203_1021"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="declaracao",
            options={"ordering": ("-ano_base", "-retificadora")},
        ),
        migrations.AddField(
            model_name="dialect",
            name="last_dirf_file",
            field=models.ForeignKey(
                blank=True, to="ged.Arquivo", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="dialect",
            name="last_processed_summary",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="declaracao",
            name="rectified_receipt",
            field=models.CharField(
                default=b"",
                max_length=12,
                verbose_name=b"Recibo retificado",
                blank=True,
            ),
        ),
    ]
