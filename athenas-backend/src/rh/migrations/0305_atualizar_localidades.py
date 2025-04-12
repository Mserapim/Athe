from django.db import migrations, models

from rh.models import Estado, Localidade


def forward(*args, **kwargs):
    sao_paulo = Estado.objects.get(pk=74)
    Localidade.objects.filter(pk__in=[11578, 11687, 11791, 11888]).update(
        estado=sao_paulo
    )


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0304_atualizar_mov_subs_pagos"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
