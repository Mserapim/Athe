from django.db import migrations
from django.conf import settings
from django.core.management import call_command
import os


FIXTURES = ("fixtures/0006_tipo_solicitante.json",)


def forward(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "diarias", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("diarias", "0003_auto_20240506_1922"),
    ]

    operations = [migrations.RunPython(forward, backward)]
