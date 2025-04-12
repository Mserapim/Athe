from django.db import migrations
from django.conf import settings
from django.core.management import call_command
import os


FIXTURES = (
    "fixtures/0001_motivo_viagem.json",
    "fixtures/0002_finalidade_viagem.json",
    "fixtures/0003_situacao_viagem.json",
    "fixtures/0004_etapa_viagem.json",
    "fixtures/0005_acomp_autoridade.json",
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
        ("diarias", "0001_rm_parametros_antigos"),
    ]

    operations = [migrations.RunPython(forward, backward)]
