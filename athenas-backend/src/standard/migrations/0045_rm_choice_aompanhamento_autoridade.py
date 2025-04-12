from django.db import migrations

from standard.models import Choice


def forward(*args, **kwargs):
    print("Running forward...")

    Choice.objects.filter(name="ACOMPANHAMENTO_AUTORIDADE").delete()


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0044_load_fixture_acomp_autoridade"),
    ]

    operations = [migrations.RunPython(forward, backward)]
