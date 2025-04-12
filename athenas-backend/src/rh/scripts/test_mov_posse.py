# -*- coding: utf-8 -*-
"""
    Este script migra Colaboradores para PossessionCollaborator e PossessionTraine.
    Este script migra Declaração de Atividade para Designação de Exercício.
"""

import django
import os


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()


from contrib.utils import getLogger
from contrib.middleware import set_current_user
from rh.models import MovimentacaoPosse


log = getLogger(__name__)


set_current_user("athenas")


def run():
    query = MovimentacaoPosse.objects.filter()
    total = query.count()
    count = 0
    for p in query.order_by("-data_exercicio"):
        try:
            p = p.my_origin
            p.save()
            count += 1
        except Exception as err:
            print(p)
            print(err)
            print("------------------------")
        log.info(f"{count} of {total}")


if __name__ == "__main__":
    run()
