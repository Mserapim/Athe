# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0045_collect_outcourtlawsuit_log"),
    ]

    operations = [
        migrations.CreateModel(
            name="RemittanceItselfOrgan",
            fields=[
                (
                    "partlawsuit_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("text", models.TextField()),
                (
                    "department",
                    models.ForeignKey(
                        to="rh.Lotacao", on_delete=django.db.models.deletion.PROTECT
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
    ]
