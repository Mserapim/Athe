# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models
from datetime import datetime


def migrate_active_functional_status(apps, schema_editor):
    FunctionalSituation = apps.get_model("rh", "SituacaoFuncional")
    updated = 0
    today = datetime.now().date()
    for fs in FunctionalSituation.objects.filter():
        active = True
        if fs.data_inicio > today:
            active = False
        if fs.data_fim and fs.data_fim < today:
            active = False

        if fs.active != active:
            FunctionalSituation.objects.filter(pk=fs.pk).update(active=active)
            updated += 1

    print("\nSituacaoFuncional UPDATED: %d" % updated)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0097_auto_20191004_1302"),
    ]

    operations = [
        migrations.RunPython(migrate_active_functional_status, _null_function),
    ]
