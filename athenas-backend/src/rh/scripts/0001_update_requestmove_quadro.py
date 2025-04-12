# -*- coding: utf-8 -*-
"""
    Este script atualiza o quadro de RequestMove com base no quadro da posse_origem, caso tenha.
"""

import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.models import RequestMove

log = getLogger(__name__)


set_current_user("athenas")


def run():
    print(
        """

        Este script atualiza o quadro de RequestMove com base no quadro da posse_origem, caso tenha.

    """
    )
    for rm in RequestMove.objects.filter(
        quadro__isnull=True, possession_origin__isnull=False
    ):
        ups = RequestMove.objects.filter(pk=rm.pk).update(
            quadro=rm.possession_origin.quadro
        )
        print(f'{"OK" if ups else "ERRO"} - {rm.servidor} - {rm}')


if __name__ == "__main__":
    run()
