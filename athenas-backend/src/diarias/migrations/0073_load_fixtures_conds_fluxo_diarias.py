from django.db import migrations
from django.conf import settings
from django.core.management import call_command
import os

from diarias.models import CondicionalFluxoViagem, FluxoViagem


FIXTURES = ("fixtures/0025_fluxo_viagem_novos.json",)


def forward(*args, **kwargs):
    print("Running forward...")

    BASE_DIR = getattr(settings, "BASE_DIR", "")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "diarias", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("diarias", "0072_load_fixtures_fluxo_viagem"),
    ]

    operations = [migrations.RunPython(forward, backward)]
