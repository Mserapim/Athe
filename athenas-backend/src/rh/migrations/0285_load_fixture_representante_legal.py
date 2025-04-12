from django.db import migrations
from django.conf import settings
from django.core.management import call_command

import os

FIXTURES = ("fixtures/TIPO_REPRESENTANTE_LEGAL.json",)


def forward(apps, schema_editor):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "rh", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [("rh", "0284_auto_20231025_2315")]

    operations = [
        migrations.RunPython(forward, backward),
    ]
