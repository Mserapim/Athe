from django.db import migrations
from django.conf import settings
from django.core.management import call_command
import os

from diarias.models import CondicionalFluxoViagem, FluxoViagem


FIXTURES = (
    "fixtures/0018_fluxo_viagem_novos.json",
    "fixtures/0019_conds_fluxo_diarias.json",
)


def forward(*args, **kwargs):
    print("Running forward...")

    CondicionalFluxoViagem.objects.filter().delete()

    BASE_DIR = getattr(settings, "BASE_DIR", "")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "diarias", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("diarias", "0054_auto_20240904_1902"),
    ]

    operations = [migrations.RunPython(forward, backward)]
