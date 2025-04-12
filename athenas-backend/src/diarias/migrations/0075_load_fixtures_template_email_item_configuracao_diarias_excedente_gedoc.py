from django.db import migrations
from django.conf import settings
from django.core.management import call_command
import os


FIXTURES = (
    "fixtures/0026_template_email_solicitacao_diaria_excedente_gedoc.json",
    "fixtures/0027_item_configuracao_emails_gedcoc_excedentes.json",
)


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
        ("diarias", "0074_atualizacao_cond_fluxo"),
    ]

    operations = [migrations.RunPython(forward, backward)]
