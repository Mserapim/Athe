from django.db import migrations
from django.conf import settings
from django.core.management import call_command
import os


FIXTURES = ("fixtures/0020_convenio_bb.json",)


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
        ("gfp", "0130_bankingconvenant_chave_pix"),
        ("diarias", "0065_auto_20240920_1803"),
    ]

    operations = [migrations.RunPython(forward, backward)]
