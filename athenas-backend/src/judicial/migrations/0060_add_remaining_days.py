# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from datetime import date


def up_count_days(apps, schema_editor):

    OutCourtLawsuit = apps.get_model("judicial.OutCourtLawsuit")
    Manifestation = apps.get_model("judicial.Manifestation")

    print("Atualizando remaining_days de OutCourtLawsuit...")

    for lawsuit in OutCourtLawsuit.objects.filter():
        days = (
            (lawsuit.deadline_cache - date.today()).days
            if lawsuit.deadline_cache
            else None
        )
        OutCourtLawsuit.objects.filter(pk=lawsuit.pk).update(remaining_days=days)

    print("Atualizando remaining_days de Manifestacao...")

    for manifestation in Manifestation.objects.filter():
        days = (
            (manifestation.deadline - date.today()).days
            if manifestation.deadline
            else None
        )
        Manifestation.objects.filter(pk=manifestation.pk).update(remaining_days=days)


def down_count_days(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0059_attached_number_pages"),
    ]

    operations = [
        migrations.AddField(
            model_name="manifestation",
            name="remaining_days",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="outcourtlawsuit",
            name="remaining_days",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.RunPython(up_count_days, down_count_days),
    ]
