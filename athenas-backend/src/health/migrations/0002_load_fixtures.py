import os

from django.conf import settings
from django.core.management import call_command
from django.db import migrations

FIXTURES = (
    "fixtures/0001_choices.json",
    "fixtures/0002_diagnosisprocedure.json",
)


def forward(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "health", fixture)
        print('\033[1mRunning loaddata for "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("health", "0001_initial"),
    ]

    operations = [migrations.RunPython(forward, backward)]
