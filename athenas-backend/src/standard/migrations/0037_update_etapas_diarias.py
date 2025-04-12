# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations

from standard.models import Choice


def forward(*args, **kwargs):
    print("Running forward...")

    Choice.objects.filter(name="ETAPA_SOLICITACAO_VIAGEM", value=7).update(
        label="Sub ADM"
    )
    Choice.objects.filter(name="ETAPA_SOLICITACAO_VIAGEM", value=8).update(
        label="Assessoria da Sub ADM"
    )


def backward(*args, **kwargs):
    print("Running backward...")

    Choice.objects.filter(name="ETAPA_SOLICITACAO_VIAGEM", value=7).update("Sub")
    Choice.objects.filter(name="ETAPA_SOLICITACAO_VIAGEM", value=8).update(
        "Assessoria da Sub"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0036_load_fixture_01119_exclude_niveis_cargos"),
    ]

    operations = [migrations.RunPython(forward, backward)]
