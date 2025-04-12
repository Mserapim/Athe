# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models.query_utils import Q
from rh.ferias.models import PeriodoAquisitivoServidorUsufruto

import django.db.models.deletion

import sys


def _null_function(apps, schema_editor):
    pass


def migrate_fields(apps, schema_editor):
    query = PeriodoAquisitivoServidorUsufruto.objects.filter(data_fim_cache=None)
    print("TOTAL ... %s" % query.count())
    count = 1
    for pasu in query:
        print("UPDATING ... %s" % count)
        PeriodoAquisitivoServidorUsufruto.objects.filter(pk=pasu.pk).update(
            data_fim_cache=pasu.data_fim
        )
        count += 1
    print("OK")


class Migration(migrations.Migration):

    dependencies = [
        ("ferias", "0005_auto_20180405_1203"),
    ]

    operations = [
        migrations.RunPython(migrate_fields, _null_function),
    ]
