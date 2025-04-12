# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.management import call_command
from django.db import migrations

FIXTURES = ("common/services/fixtures/folhaponto_import_batidas_scheduleservice.json",)


def forward(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0008_load_folhaponto_import_justif_scheduledservice"),
        ("standard", "0031_load_folhaponto_import_batidas_classcode"),
    ]

    operations = [migrations.RunPython(forward, backward)]
