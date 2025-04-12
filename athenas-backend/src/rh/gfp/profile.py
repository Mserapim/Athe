# -*- coding: utf-8 -*-

import django
import os


from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.gfp.dirf.models import Dialect

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
# from contrib.decorator import profile

log = getLogger(__name__)


# @profile('recalculate.prof')
def profile_recalculate():
    from rh.gfp.models import ContraCheque

    cc = ContraCheque.objects.get(folha=816, servidor__matricula=91108)
    cc.recalculate()


# @profile('dirf.prof')
def profile_summary_dirf():
    # log.info('INIT PROFILE --------------------------')
    set_current_user("raysonsilva")
    dialect = Dialect.objects.get(calendar_year=2018)
    dialect.summarize_entries()
    # log.info('ENDING PROFILE --------------------------')


if __name__ == "__main__":
    django.setup()
    profile_summary_dirf()
