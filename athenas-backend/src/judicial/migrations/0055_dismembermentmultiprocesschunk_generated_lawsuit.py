# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def up(apps, schema_editor):
    DismembermentMultiProcess = apps.get_model("judicial", "DismembermentMultiProcess")

    for dm in DismembermentMultiProcess.objects.filter():
        for shared in dm.shared_with_lawsuit.filter():
            dm.chunks.filter(change_title=shared.title).update(
                generated_lawsuit=dm.lawsuit
            )


def down(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0054_legalclassification_extend_deadline"),
    ]

    operations = [
        migrations.AddField(
            model_name="dismembermentmultiprocesschunk",
            name="generated_lawsuit",
            field=models.ForeignKey(
                related_name="in_dismemberment_process_chunck",
                blank=True,
                to="judicial.OutCourtLawsuit",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.RunPython(up, down),
    ]
