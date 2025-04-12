from django.db import migrations

from standard.models import Choice


def forward(*args, **kwargs):
    print("Running forward...")

    Choice.objects.filter(name="CONDICIONAIS_FLUXO_DIARIAS", value=12).update(
        description="resp_lotacao-53012,52344"
    )
    Choice.objects.filter(name="CONDICIONAIS_FLUXO_DIARIAS", value=13).update(
        description="resp_lotacao-52645"
    )
    Choice.objects.filter(name="CONDICIONAIS_FLUXO_DIARIAS", value=14).update(
        description="nao_resp_lotacao-52645"
    )
    Choice.objects.filter(name="CONDICIONAIS_FLUXO_DIARIAS", value=15).update(
        description="nao_resp_lotacao-52344"
    )


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0041_update_condicionais_descr"),
    ]

    operations = [migrations.RunPython(forward, backward)]
