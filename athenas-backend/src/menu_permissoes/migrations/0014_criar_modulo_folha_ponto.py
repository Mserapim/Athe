from django.db import migrations
from django.conf import settings
from django.core.management import call_command
import os


FIXTURES = ("fixtures/modulo_menu_folha_ponto.json",)


def forward(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "menu_permissoes", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("menu_permissoes", "0013_criar_grupo_acesso_vdf_padrao"),
    ]

    operations = [migrations.RunPython(forward, backward)]
