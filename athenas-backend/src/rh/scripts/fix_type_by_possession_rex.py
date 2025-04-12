# -*- coding: utf-8 -*-
"""

"""

import os
from datetime import timedelta

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.models import RequestMove, Servidor

log = getLogger(__name__)


set_current_user("athenas")


def run():
    print(
        """

        Este script corrige type_by_possession de requisitados.

    """
    )

    print("Atualizando RequestMove de policiais militares EXT para REX:")
    query = RequestMove.objects.filter(
        servidor__type_by_possession="EXT", job_position_origin__icontains="MILITAR"
    )
    for mr in query:
        print(mr.servidor, mr)
    print(
        Servidor.objects.filter(pk__in=query.values_list("servidor", flat=True)).update(
            type_by_possession="REX"
        )
    )

    print("Atualizando RequestMove de servidores EXT para REQ:")
    query = RequestMove.objects.filter(servidor__type_by_possession="EXT")
    for mr in query:
        print(mr.servidor, mr)
    print(
        Servidor.objects.filter(pk__in=query.values_list("servidor", flat=True)).update(
            type_by_possession="REQ"
        )
    )

    print(
        "Solicita atualização de exercise_date de servidores que possuem data_exercicio diferente de exercise_date:"
    )
    for s in Servidor.objects.filter():
        if s.data_exercicio != s.exercise_date:
            print(s.data_exercicio, s.exercise_date, s)
            s.save()

    print(
        "Atualiza possession_origin_date de RequestMove quando não for preenchida ou for maior que exercise_date do servidor:"
    )
    query = RequestMove.objects.filter()
    for mr in query.order_by("servidor"):
        if (
            not mr.possession_origin_date
            or mr.possession_origin_date >= mr.servidor.exercise_date
        ):
            print(mr.servidor, mr)
            print(
                query.filter(pk=mr.pk).update(
                    possession_origin_date=mr.servidor.exercise_date - timedelta(days=1)
                )
            )


if __name__ == "__main__":
    run()
