# -*- coding: utf-8 -*-
from django.db import migrations
from django.core.management import call_command
from django.conf import settings
import os


FIXTURES = ("fixtures/tipos_processametos_choices.json",)


def forward(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "engine", "mq", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("mq", "0007_task_tipo_processamento"),
    ]

    operations = [migrations.RunPython(forward, backward)]
