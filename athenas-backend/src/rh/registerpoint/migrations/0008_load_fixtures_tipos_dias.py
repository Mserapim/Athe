# -*- coding: utf-8 -*-
from django.db import migrations
from django.core.management import call_command
from django.conf import settings
import os


FIXTURES = ("fixtures/tipos_dias_choices.json",)


def forward(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "rh", "registerpoint", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("registerpoint", "0007_auto_20240223_1211"),
    ]

    operations = [migrations.RunPython(forward, backward)]
