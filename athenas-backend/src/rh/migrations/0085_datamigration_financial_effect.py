# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models
from datetime import datetime


def migrate_financial_effect_date(apps, schema_editor):
    MovimentacaoPosseModel = apps.get_model("rh", "MovimentacaoPosse")
    updated = 0
    for mov in MovimentacaoPosseModel.objects.filter(financial_effect_date=None):
        MovimentacaoPosseModel.objects.filter(pk=mov.pk).update(
            financial_effect_date=mov.data_exercicio
        )
        updated += 1
    print("\nMOVIMENTACAOPOSSE UPDATED: %d" % updated)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0084_auto_20190410_1420"),
    ]

    operations = [
        migrations.RunPython(migrate_financial_effect_date, _null_function),
    ]
