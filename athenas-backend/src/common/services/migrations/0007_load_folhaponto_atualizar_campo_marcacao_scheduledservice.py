# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.management import call_command
from django.db import migrations

FIXTURES = ("common/services/fixtures/folhaponto_atualizar_marc_scheduledservice.json",)


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
        ("services", "0006_load_fixtures_scheduledservice_resident"),
        ("standard", "0029_load_folhaponto_atualizar_campo_marcacao_classcode"),
    ]

    operations = [migrations.RunPython(forward, backward)]
