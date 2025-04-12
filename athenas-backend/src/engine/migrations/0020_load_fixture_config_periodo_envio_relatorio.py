# -*- coding: utf-8 -*-
from django.db import migrations
from django.conf import settings
from django.core.management import call_command

import os

FIXTURES = ("fixtures/config_periodo_envio_relatorio_teletrabalho.json",)


def forward(apps, schema_editor):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "engine", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [("engine", "0019_load_fixture_teletrabalho_menu")]

    operations = [
        migrations.RunPython(forward, backward),
    ]
