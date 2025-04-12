from django.db import migrations

from contrib.middleware import set_current_user
from rh.models import Localidade, Estado


def forward(*args, **kwargs):
    set_current_user("athenas")

    # PA - Mojuí dos Campos - 1504752
    Localidade.objects.create(
        estado=Estado.objects.get(sigla="PA"),
        nome="Mojuí dos Campos",
        ibge="1504752",
        indicador_municipio=True,
    )

    # PI - Nazária - 2206720
    Localidade.objects.create(
        estado=Estado.objects.get(sigla="PI"),
        nome="Nazária",
        ibge="2206720",
        indicador_municipio=True,
    )

    # SC - Balneário Rincão - 4220000
    Localidade.objects.create(
        estado=Estado.objects.get(sigla="SC"),
        nome="Balneário Rincão",
        ibge="4220000",
        indicador_municipio=True,
    )

    # SC - Pescaria Brava - 4212650
    Localidade.objects.create(
        estado=Estado.objects.get(sigla="SC"),
        nome="Pescaria Brava",
        ibge="4212650",
        indicador_municipio=True,
    )

    # RS - Pinto Bandeira - 4314548
    Localidade.objects.create(
        estado=Estado.objects.get(sigla="RS"),
        nome="Pinto Bandeira",
        ibge="4314548",
        indicador_municipio=True,
    )

    # MS - Paraíso das Águas - 5006275
    Localidade.objects.create(
        estado=Estado.objects.get(sigla="MS"),
        nome="Paraíso das Águas",
        ibge="5006275",
        indicador_municipio=True,
    )


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0308_auto_20240705_1202"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
