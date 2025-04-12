# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0048_personhasaccess_controlled"),
    ]

    operations = [
        migrations.AlterField(
            model_name="outcourtlawsuit",
            name="title",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="judicialdiligence",
            name="part",
            field=models.ForeignKey(
                related_name="diligences",
                to="judicial.PartLawsuit",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
