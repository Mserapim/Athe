# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0018_auto_20181226_1843"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="deadlinerecommendation",
            options={
                "ordering": ["id"],
                "verbose_name": "Recomenda\xe7\xf5es gerais na inspe\xe7\xe3o",
            },
        ),
        migrations.AlterModelOptions(
            name="recommendations",
            options={
                "ordering": ["id"],
                "verbose_name": "Recomenda\xe7\xf5es gerais na inspe\xe7\xe3o",
            },
        ),
        migrations.AlterField(
            model_name="administrativeorganizationregistrationsystem",
            name="registration_type",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Tipo de Registro",
                blank=True,
                choices=[
                    (1, "Manual"),
                    (2, "Informatizado"),
                    (3, "Manual/Informatizado"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="existingregisters",
            name="registration_type",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Tipo de Registro",
                blank=True,
                choices=[
                    (1, "Manual"),
                    (2, "Informatizado"),
                    (3, "Manual/Informatizado"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="attendance",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="daily_attendance",
            field=models.BooleanField(default=False),
        ),
    ]
