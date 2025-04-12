# -*- coding: utf-8 -*-
from django.db import migrations
from django.conf import settings
from django.core.management import call_command

import os

FIXTURES = ("fixtures/config_periodo_vendas_cumulativo_substituicoes.json",)


def up(apps, schema_editor):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "engine", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def down(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [("engine", "0013_auto_20230630_1816")]

    operations = [
        migrations.RunPython(up, down),
    ]
