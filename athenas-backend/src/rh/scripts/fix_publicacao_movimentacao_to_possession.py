# -*- coding: utf-8 -*-
"""
    Este script corrige as publicações de movimentação dos colaboradores.
    Escrevendo as publicações que estão em DeclaracaoAtividade para PossessionCollaborator.
"""

import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.models import DeclaracaoAtividade, PossessionCollaborator


log = getLogger(__name__)


set_current_user("athenas")


def run():
    print(
        """
    Este script corrige as publicações de movimentação dos colaboradores.
    Escrevendo as publicações que estão em DeclaracaoAtividade para PossessionCollaborator.
    """
    )

    query = PossessionCollaborator.objects.filter(publicacao_movimentacao__isnull=True)
    total = query.count()
    count = 0
    for possession in query:
        da = DeclaracaoAtividade.objects.filter(
            servidor=possession.servidor, data_exercicio=possession.data_exercicio
        ).last()
        if da and da.publicacao_movimentacao:
            print(da.publicacao_movimentacao)
            PossessionCollaborator.objects.filter(pk=possession.pk).update(
                publicacao_movimentacao=da.publicacao_movimentacao
            )
            count += 1
            print(f"{count} of {total}")

    print(
        total,
        PossessionCollaborator.objects.filter(
            publicacao_movimentacao__isnull=True
        ).count(),
    )


if __name__ == "__main__":
    run()
