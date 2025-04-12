# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from adm.patrimonio.models import Avaliacao, NotaBaixa
from contrib.middleware import set_current_user
from django.db import migrations, transaction


def forwards_data_migration(apps, schema_editor):
    """
    Reversão de dados de bens patrimoniais referente à revisão 1103:c416e5f9c82b
    no que tange o arquivo patrimonio/models.py no repositório adm.
    """

    set_current_user("athenas")
    FAILURE_START = datetime(2017, 1, 16)

    erroed_assets = []
    pkset = []

    for nb in NotaBaixa.objects.filter(state=2, data_baixa__gte=FAILURE_START):
        for bi in nb.itens.filter(patrimonio__avaliacoes__avaliacao__tipo=4):
            ai = bi.patrimonio.avaliacoes.get(avaliacao__tipo=4)
            ai.patrimonio.valor_atual = ai.valor_atual
            try:
                with transaction.atomic():
                    ai.patrimonio.save()
                    print(ai.patrimonio)
            except Exception:
                erroed_assets.append(ai)
            else:
                a = ai.avaliacao
                ai.delete()
                pkset.append(a.pk)

    # Apagando as 'Reversões de Depreciação' que tenham ficado vazias
    pkset = set(pkset)
    Avaliacao.objects.filter(pk__in=pkset).delete()

    print("\nErrados: ", erroed_assets)


def reverse_data_migration(apps, schema_editor):
    """
    Desfazimento das ações executadas por essa migração
    Não há meio de reverter a exclusão dos dados dessa
    reversão de depreciação
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("patrimonio", "0012_add_valor_base_in_patrimonio"),
    ]

    operations = [migrations.RunPython(forwards_data_migration, reverse_data_migration)]
