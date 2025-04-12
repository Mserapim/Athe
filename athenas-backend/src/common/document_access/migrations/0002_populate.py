# -*- coding: utf-8 -*-
import os

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth.management import create_permissions
from django.db import migrations
from django.core.management import call_command

FIXTURES = (
    "01-menu-application.json",
    "02-menu-controller.json",
    "03-choices.json",
    "04-controltypes.json",
    "05-legalprerogative.json",
)


def up_load_initial_data(apps, schema_editor):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("\n\n", "*** LOADING INITIAL DATA ***")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "common/document_access/fixtures", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def up_fix_permission(apps, schema_editos):
    print("\n", "*** CREATING PERMISSIONS ***")
    AppConfig = django_apps.get_app_config("document_access")
    create_permissions(AppConfig, verbosity=3)


def down_empty(apps, schema_editos):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("document_access", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(up_fix_permission, down_empty),
        migrations.RunPython(up_load_initial_data, down_empty),
    ]
