# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_demonstrativo_version(apps, schema_editor):

    Declaration = apps.get_model("dirf", "Declaracao")
    print("")
    for d in Declaration.objects.all().order_by("ano_base", "retificadora"):
        count = d.demonstrativos.update(version=d.retificadora)
        print("Updating statements of income tax for %s (%d) OK" % (d.nome, count))


def null_method(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dirf", "0008_auto_20160219_0742"),
    ]

    operations = [
        migrations.RunPython(update_demonstrativo_version, null_method),
    ]
