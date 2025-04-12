# -*- coding: utf-8 -*-
from django.db import migrations
from django.conf import settings
from django.core.management import call_command

import os

from rh.gfp.models import FolhaEvento

FIXTURES = ("gfp/fixtures/entry_insertion_type_options.json",)


def up(apps, schema_editor):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "rh", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)

    FolhaEvento.objects.filter(automated=True).update(insertion_type=1)
    FolhaEvento.objects.filter(automated=False).update(insertion_type=2)


def down(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [("gfp", "0111_auto_20230419_1301")]

    operations = [
        migrations.RunPython(up, down),
    ]
