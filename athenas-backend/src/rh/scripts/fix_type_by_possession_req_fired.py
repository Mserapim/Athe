# -*- coding: utf-8 -*-
"""
    Este script migra MovimentacaoRequisicao para RequestMove.
"""

import os

import django
from dateutil.relativedelta import relativedelta

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger

from rh.models import MovimentacaoRequisicao

log = getLogger(__name__)


set_current_user("athenas")


def run():
    print(
        """

        Este script corrige type_by_possession de requisitados inativos.

    """
    )

    query = MovimentacaoRequisicao.objects.filter(
        onus=2, servidor__ativo=False, servidor__type_by_possession="EXT"
    )  # servidor__matricula=112178551)
    total = query.count()
    count = 0
    for mr in query:
        mr.servidor._update_type_by_possession()
        print(mr.servidor, mr)
        count += 1
        print(f"{count} of {total}")


if __name__ == "__main__":
    run()
