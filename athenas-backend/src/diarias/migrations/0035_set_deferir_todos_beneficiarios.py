from django.db import migrations
from django.conf import settings
from django.core.management import call_command
import os

from diarias.models import FluxoViagem


FIXTURES = ("fixtures/0001_motivo_viagem.json",)


def forward(*args, **kwargs):
    # atualizando registros de FluxoViagem que devem ter o campo 'deferir_todos_beneficiarios' com valor True
    # Os fluxo que devem ser alterados são:
    # id: 10 - DEPLAN- Gestor - Aguardando assinatura empenho
    # id: 11 - DG - Aguardando assinatura Ordenador de Despesas

    FluxoViagem.objects.filter(id__in=[10, 11]).update(deferir_todos_beneficiarios=True)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("diarias", "0034_auto_20240709_1456"),
    ]

    operations = [migrations.RunPython(forward, backward)]
