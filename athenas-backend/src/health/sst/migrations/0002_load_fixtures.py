import os

from django.conf import settings
from django.core.management import call_command
from django.db import migrations

FIXTURES = (
    "fixtures/0001_choices.json",
    "fixtures/0002_causeragent.json",
    "fixtures/0003_causeragentaccident.json",
    "fixtures/0004_bodypart.json",
    "fixtures/0005_injury.json",
    "fixtures/0006_harmfulagent.json",
    "fixtures/initialdb_0001_applications.json",
    "fixtures/initialdb_0002_contenttypes.json",
    "fixtures/initialdb_0003_permissions.json",
    "fixtures/initialdb_0004_groups.json",
    "fixtures/initialdb_0005_controllers.json",
    "fixtures/initialdb_0006_controllerpermissions.json",
)


def forward(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "health", "sst", fixture)
        print('\033[1mRunning loaddata for "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("sst", "0001_initial"),
    ]

    operations = [migrations.RunPython(forward, backward)]
