from django.db import migrations

from diarias.models import Beneficiario


def forward(*args, **kwargs):
    print("Running forward...")

    # Definindo fluxo 'Solicitante - Rascunho' para os Beneficiários que não tem fluxo.
    Beneficiario.objects.filter(fluxo__isnull=True).update(fluxo_id=2)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("diarias", "0059_auto_20240912_1109"),
    ]

    operations = [migrations.RunPython(forward, backward)]
