# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.db.models.query_utils import Q

import sys


def migrate_fields(apps, schema_editor):
    ExecutionOrganModel = apps.get_model("judicial", "ExecutionOrgan")
    query = ExecutionOrganModel.objects.filter()
    print("TOTAL ... %s" % query.count())
    count = 1
    for eo in query:
        dts = eo.in_distribution_tables.select_related("document").all()
        dt = dts.filter(end_document__isnull=True).first()
        print("UPDATING ... %s" % count)
        ExecutionOrganModel.objects.filter(pk=eo.pk).update(
            occupation_area=eo.descricao,
            attribution_document=dt.document if dt else None,
        )
        count += 1
    print("OK")


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0051_auto_20180830_1454"),
    ]

    operations = [
        migrations.RunPython(migrate_fields, _null_function),
    ]
