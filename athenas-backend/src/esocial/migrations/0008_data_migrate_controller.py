# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
from django.db import migrations
from django.conf import settings
from django.core.management import call_command


FIXTURES = ("fixtures/initialdb_0003_controllers.json",)


def load_fixture(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running initial data...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "esocial", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("esocial", "0007_auto_20211001_1759"),
    ]

    operations = [
        migrations.RunPython(
            code=load_fixture,
            reverse_code=_null_function,
        ),
    ]
