# -.- coding: utf-8 -.-
"""
    Este módulo possui 3 funções para checar se o existe Usufruto correspondente ao Afastamento.

    call_check_period_recess
    call_check_period_electoral_slack
    call_check_period_birthday_break

    Para rodar:
        python rh/dayoff/scripts/diff_departure_dayoff.py
"""


import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from rh.const import CANCELED
from rh.dayoff.models import Usufruct
from rh.dayoff.const import USU_CANCELED
from rh.afastamento.models import FolgaAniversario, Recesso, FolgaEleitoral

from contrib.utils import getLogger

log = getLogger(__name__)


def check_period(departure):
    acquisition_period = Usufruct.objects.filter(
        activity__acquisition_period__employee=departure.servidor,
        start_date=departure.data_inicio,
        end_date=departure.data_fim,
    )
    if not acquisition_period.exclude(status=USU_CANCELED).exists():
        print(
            f"NÃO EXISTE USUFRUTO | {departure.ano} | {departure.__str_restful__()} | {departure.servidor} | {acquisition_period.count()}"
        )


def call_check_period_recess():
    query = Recesso.objects.filter(servidor__tipo__in=["S", "M"]).exclude(
        estado=CANCELED
    )
    total = query.count()
    count = 0
    # print(f'{count} of {total}')
    for departure in query.order_by("-ano"):
        count += 1
        year_map = {
            "213/2014": 2013,
            "2007/2008": 2007,
            "2008/2009": 2008,
            "2009/2010": 2009,
            "2010/2011": 2010,
            "2011/2012": 2011,
            "2012/2013": 2012,
            "2013/2014": 2013,
            "2014/2015": 2014,
            "2015/2016": 2015,
            "2015/2015": 2015,
            "20162017": 2016,
            "20152018": 2018,
            "2011/2013": 2011,
        }
        year = year_map.get(departure.ano, departure.ano)
        try:
            check_period(departure)
        except Exception as err:
            print(err)
            print(f"{departure.ano} | {departure.servidor} | {departure}")


def call_check_period_electoral_slack():
    FolgaEleitoral.objects.filter(ano=210).update(ano=2010)
    query = FolgaEleitoral.objects.filter(servidor__tipo__in=["S", "M"]).exclude(
        estado=CANCELED
    )
    total = query.count()
    count = 0
    # print(f'{count} of {total}')
    for departure in query.order_by("-ano", "data_inicio", "servidor"):
        count += 1
        try:
            check_period(departure)
        except Exception as err:
            print(err)
            print(f"{departure.ano} | {departure.servidor} | {departure}")
        # print(f'{count} of {total}')


def call_check_period_birthday_break():
    query = FolgaAniversario.objects.filter(ano__in=[2020, 2021]).exclude(
        estado=CANCELED
    )
    total = query.count()
    count = 0
    # print(f'{count} of {total}')
    for departure in query.order_by("-ano", "data_inicio", "servidor"):
        count += 1
        try:
            check_period(departure)
        except Exception as err:
            print(err)
            print(f"{departure.ano} | {departure.servidor} | {departure}")
        # print(f'{count} of {total}')


def run():
    call_check_period_recess()
    call_check_period_electoral_slack()
    call_check_period_birthday_break()


if __name__ == "__main__":
    run()
