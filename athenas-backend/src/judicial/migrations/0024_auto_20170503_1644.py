# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def up_fn(apps, schema_editor):
    PartLawsuitAccess = apps.get_model("judicial.PartLawsuitAccess")
    for pla in PartLawsuitAccess.objects.filter(lawsuit=None):
        PartLawsuitAccess.objects.filter(pk=pla.pk).update(lawsuit=pla.part.lawsuit)


def down_fn(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0023_auto_20170424_1525"),
    ]

    operations = [
        migrations.AddField(
            model_name="partlawsuitaccess",
            name="lawsuit",
            field=models.ForeignKey(
                related_name="access_controls",
                blank=True,
                to="judicial.OutCourtLawsuit",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="partlawsuitaccess",
            name="part",
            field=models.ForeignKey(
                related_name="access_controls",
                blank=True,
                to="judicial.PartLawsuit",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.RunPython(up_fn, down_fn),
    ]
