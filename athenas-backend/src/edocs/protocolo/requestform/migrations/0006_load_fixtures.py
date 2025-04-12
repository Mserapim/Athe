import os

from django.conf import settings
from django.core.management import call_command
from django.db import migrations

FIXTURES = ("fixtures/employee-request.json",)


def forward(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "edocs", "protocolo", "requestform", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("requestform", "0005_employeerequest"),
    ]

    operations = [migrations.RunPython(forward, backward)]
