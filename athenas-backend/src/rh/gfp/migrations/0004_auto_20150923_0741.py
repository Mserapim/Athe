# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_quantidade_max(apps, schema_editor):

    Event = apps.get_model("gfp", "Evento")
    Event.objects.filter(quantidade_max__isnull=True).update(quantidade_max=0)


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0003_auto_20150902_1133"),
    ]

    operations = [
        migrations.RunPython(update_quantidade_max),
    ]
