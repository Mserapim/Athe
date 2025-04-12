# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0037_legalclassification_selectable"),
    ]

    operations = [
        migrations.AddField(
            model_name="outcourtlawsuit",
            name="last_part_lawsuit",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="judicial.PartLawsuit",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
