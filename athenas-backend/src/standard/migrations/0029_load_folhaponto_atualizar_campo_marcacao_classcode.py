# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.management import call_command
from django.db import migrations

FIXTURES = ("fixtures/folhaponto_atualizar_marc_classcode.json",)


def forward(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "standard", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0028_load_folhaponto_tipo_justificativa_choice_fixtures"),
    ]

    operations = [migrations.RunPython(forward, backward)]
