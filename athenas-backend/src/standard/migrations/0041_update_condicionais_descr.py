from django.db import migrations

from standard.models import Choice


def forward(*args, **kwargs):
    print("Running forward...")

    Choice.objects.filter(name="CONDICIONAIS_FLUXO_DIARIAS", value=23).update(
        description="etapa_anterior-33"
    )
    Choice.objects.filter(name="CONDICIONAIS_FLUXO_DIARIAS", value=24).update(
        description="etapa_anterior-24"
    )
    Choice.objects.filter(name="CONDICIONAIS_FLUXO_DIARIAS", value=25).update(
        description="etapa_anterior-28"
    )
    Choice.objects.filter(name="CONDICIONAIS_FLUXO_DIARIAS", value=26).update(
        description="etapa_anterior-26"
    )
    Choice.objects.filter(name="CONDICIONAIS_FLUXO_DIARIAS", value=27).update(
        description="etapa_anterior-6"
    )


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0040_update_etapas_descr"),
    ]

    operations = [migrations.RunPython(forward, backward)]
