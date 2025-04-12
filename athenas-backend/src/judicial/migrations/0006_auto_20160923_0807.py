# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0005_attached_attached_diligence"),
    ]

    operations = [
        migrations.AddField(
            model_name="outcourtlawsuit",
            name="external_location",
            field=models.ForeignKey(
                related_name="in_lawsuit_as_external",
                blank=True,
                to="rh.OrgaoGeral",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="triage",
            name="triage_number",
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="triage",
            name="triage_year",
            field=models.IntegerField(blank=True),
        ),
    ]
