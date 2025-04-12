# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core.management import call_command
from django.conf import settings

import os

FIXTURES = ("fixtures/choices_organizational_classification.json",)


def load_fixture(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Loading fixture...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "rh", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0074_auto_20181218_1933"),
    ]

    operations = [migrations.RunPython(load_fixture, _null_function)]
