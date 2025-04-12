# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models
from datetime import datetime


def migrate_interrupt_vacation(apps, schema_editor):
    print("ATUALIZACAO DE AFASTAMENTOS interrupt_vacation")
    BaseLicencaAfastamentoModel = apps.get_model(
        "afastamento", "BaseLicencaAfastamento"
    )
    updated = 1
    movs = BaseLicencaAfastamentoModel.objects.filter(tipo__in=[5, 6, 39, 40])
    total = movs.count()
    for mov in movs:
        BaseLicencaAfastamentoModel.objects.filter(pk=mov.pk).update(
            interrupt_vacation=False
        )
        print(
            "ATUALIZACAO DE AFASTAMENTOS interrupt_vacation: %s de %s"
            % (updated, total)
        )
        updated += 1


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("afastamento", "0010_baselicencaafastamento_interrupt_vacation"),
    ]

    operations = [
        migrations.RunPython(migrate_interrupt_vacation, _null_function),
    ]
