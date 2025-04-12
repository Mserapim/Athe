from django.db import migrations

from standard.models import Choice
from diarias.models import CondicionalFluxoViagem


def forward(*args, **kwargs):
    print("Running forward...")

    Choice.objects.filter(name="CONDICIONAIS_FLUXO_DIARIAS", value=22).delete()
    Choice.objects.filter(name="CONDICIONAIS_FLUXO_DIARIAS", value=21).update(
        label="Beneficiário solicitou veículo institucional ao DAA",
        description="solic_veiculo_inst_ao_daa",
    )
    CondicionalFluxoViagem.objects.filter(pk=5).update(condicionais="20,21")


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0042_update_condicionais_lotacoes_descr"),
    ]

    operations = [migrations.RunPython(forward, backward)]
