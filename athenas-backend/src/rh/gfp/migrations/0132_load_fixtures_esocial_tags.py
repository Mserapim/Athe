from django.conf import settings
from django.db import migrations
from django.core.management import call_command
import os


FIXTURES = ("fixtures/esocial_tags.json",)


def forward(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "rh", "gfp", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0131_evento_banco_consignacao"),
    ]

    operations = [migrations.RunPython(forward, backward)]
