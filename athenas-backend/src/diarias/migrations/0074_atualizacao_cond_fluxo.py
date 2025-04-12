from django.db import migrations
from django.conf import settings
from django.core.management import call_command
import os

from diarias.models import CondicionalFluxoViagem


def forward(*args, **kwargs):
    print("Running forward...")

    condicional = CondicionalFluxoViagem.objects.filter(fluxo_id=3).first()
    condicional.condicionais = "1;2"
    condicional.save()


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("diarias", "0073_load_fixtures_conds_fluxo_diarias"),
    ]

    operations = [migrations.RunPython(forward, backward)]
