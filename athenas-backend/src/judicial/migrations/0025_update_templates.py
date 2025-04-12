# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.core.management import call_command


def up_fn(apps, editor_schema):
    call_command("loaddata", "judicial/fixtures/0023-glosarytemplate-update.json")


def down_fn(apps, editor_schema):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0024_auto_20170503_1644"),
    ]

    operations = [migrations.RunPython(up_fn, down_fn)]
