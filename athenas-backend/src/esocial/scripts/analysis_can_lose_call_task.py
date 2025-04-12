# -.- coding: utf-8 -.-
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from esocial.models import PayrollPeriod
from contrib.middleware import set_current_user
from rh.gfp.models import Periodo

set_current_user("gustavodettenborn")


def run():
    PayrollPeriod.analysis_call_task(period=Periodo.objects.get(mes=5, ano=2022).pk)


if __name__ == "__main__":
    run()
