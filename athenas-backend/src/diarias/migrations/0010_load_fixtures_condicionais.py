from django.db import migrations
from django.conf import settings
from django.core.management import call_command
import os


FIXTURES = (
    "fixtures/0010_fluxos_viagens.json",
    "fixtures/0011_cond_fluxos_viagens.json",
)


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
        ("diarias", "0009_auto_20240509_1834"),
    ]

    operations = [migrations.RunPython(forward, backward)]
