# -*- coding: utf-8 -*-
from django.db import migrations

from diarias.models import (
    Viagem,
    Beneficiario,
    Destino,
    HistoricoFluxoViagemBeneficiario,
    ViagemAnexo,
)


def forward(apps, schema_editor):
    print("Running forward...")
    Destino.objects.all().delete()
    HistoricoFluxoViagemBeneficiario.objects.all().delete()
    Beneficiario.objects.all().delete()
    ViagemAnexo.objects.all().delete()
    Viagem.objects.all().delete()


def backward(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [("diarias", "0085_load_fixtures_fluxo_viagem")]

    operations = [
        migrations.RunPython(forward, backward),
    ]
