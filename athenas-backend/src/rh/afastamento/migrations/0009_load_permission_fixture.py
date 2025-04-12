# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings
from django.core.management import call_command
import os

FIXTURES = (
    "fixtures/can_receive_notify_permission.json",
    "fixtures/group_can_receive_notify_permission.json",
)


def up(apps, schema_editor):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "rh", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def down(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [("afastamento", "0008_auto_20190820_1736")]

    operations = [
        migrations.RunPython(up, down),
    ]
