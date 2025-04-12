from django.db import migrations

from diarias.models import FluxoViagem


def forward(*args, **kwargs):
    FluxoViagem.objects.filter(pk__in=[2, 8]).update(calcular=True)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("diarias", "0024_auto_20240614_1721"),
    ]

    operations = [migrations.RunPython(forward, backward)]
