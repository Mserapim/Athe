# -*- coding: utf-8 -*-
from django.db import migrations

from nomeacao.models import PessoaFisicaConvidado


def up(apps, schema_editor):
    PessoaFisicaConvidado.objects.filter().update(
        orientacao_sexual=None,
        sangue_tipo=None,
        sangue_fator_rh=None,
    )


def down(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [("nomeacao", "0006_auto_20230920_0933")]

    operations = [
        migrations.RunPython(up, down),
    ]
