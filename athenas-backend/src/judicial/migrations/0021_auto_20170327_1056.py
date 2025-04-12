# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0020_auto_20170309_1408"),
    ]

    operations = [
        migrations.CreateModel(
            name="LegalClass",
            fields=[
                (
                    "legalclassification_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.LegalClassification",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("judicial.legalclassification",),
        ),
        migrations.AlterField(
            model_name="workerreminder",
            name="priority",
            field=models.SmallIntegerField(
                choices=[(1, "Normal"), (2, "Urgente"), (3, "Imediata")]
            ),
        ),
    ]
