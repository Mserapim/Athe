import os

from django.conf import settings
from django.core.management import call_command
from django.db import migrations

FIXTURES = (
    "fixtures/esocial_tags.json",
    "fixtures/esocial_genres.json",
    "fixtures/esocial_events.json",
    "fixtures/esocial_configevents.json",
)


def forward(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "rh", "gfp", fixture)
        print('\033[1mRunning loaddata for "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0102_auto_20221004_1123"),
    ]

    operations = [migrations.RunPython(forward, backward)]
