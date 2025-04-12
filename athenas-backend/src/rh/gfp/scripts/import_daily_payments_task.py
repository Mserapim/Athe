# -*- coding: utf-8 -*-
"""
    Este script corrige as publicações de movimentação dos colaboradores.
    Escrevendo as publicações que estão em DeclaracaoAtividade para PossessionCollaborator.
"""

import os

import django


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from contrib.middleware import set_current_user, get_current_user
from contrib.utils import getLogger
from rh.gfp.models import Periodo
from rh.gfp.tools.import_payroll import import_payments
from rh.gfp.tasks import import_payroll
from engine.mq.models import Task

log = getLogger(__name__)


set_current_user("athenas")


def run():
    Task.start(
        import_payroll,
        payroll_type=1,
        period=Periodo.objects.get(ano=2019, mes=1).pk,
        user=get_current_user().pk,
    )


if __name__ == "__main__":
    run()
