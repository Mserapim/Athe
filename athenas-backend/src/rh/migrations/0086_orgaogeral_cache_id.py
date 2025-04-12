# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def _null_function(apps, schema_editor):
    pass


def migrate_cache_id(apps, schema_editor):

    GeneralOrgan = apps.get_model("rh", "Orgaogeral")

    query = GeneralOrgan.objects.filter(cache_id="0")
    count = 0
    total = query.count()
    for one in query:
        count += 1
        query.filter(pk=one.pk).update(cache_id=one.pk)
        print("TOTAL ... %s - > %s" % (total, count))


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0085_datamigration_financial_effect"),
    ]

    operations = [
        migrations.AddField(
            model_name="orgaogeral",
            name="cache_id",
            field=models.CharField(
                default="0", max_length=10, verbose_name="Cache de Id"
            ),
        ),
        migrations.RunPython(migrate_cache_id, _null_function),
    ]
