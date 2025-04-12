from django.conf import settings
from django.db import migrations
from django.core.management import call_command
from rh.teletrabalho.utils import concluir_planos_teletrabalhos_sem_pendencias
import os

FIXTURES = ("fixtures/status_teletrabalho_choices.json",)


def forward(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "rh", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)

    concluir_planos_teletrabalhos_sem_pendencias()


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("teletrabalho", "0002_auto_20240109_1137"),
    ]

    operations = [migrations.RunPython(forward, backward)]
