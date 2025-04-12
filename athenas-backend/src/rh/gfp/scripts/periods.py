# -*- coding: utf-8 -*-
import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.gfp.models import Periodo


RED = "\033[0;31m"
GREEN = "\033[0;32m"
ORANGE = "\033[0;33m"
WHITE = "\033[1;37m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color


def previous_period(period, pos=1):
    fmonth = period.mes - pos
    fmonth_p = (fmonth // 13) if fmonth != 0 else -1
    month = fmonth - 13 * fmonth_p
    if month == 0:
        month = 13
        fmonth_p -= 1
    year = period.ano + fmonth_p
    p = period.__class__.objects.filter(ano=year, mes=month).last()
    return str(p) if p else "", year * 100 + month


def next_period(period, pos=1):
    fmonth = period.mes + pos
    fmonth_r = fmonth % 13
    fmonth_p = fmonth // 13
    if fmonth_r == 0:
        fmonth_p -= 1
    month = fmonth - 13 * fmonth_p
    year = period.ano + fmonth_p

    p = period.__class__.objects.filter(ano=year, mes=month).last()
    return str(p) if p else "", year * 100 + month


def np_periods(period, pos):
    p_pos = pos
    p_year = period.ano
    p_month = period.mes
    while p_pos > 0:
        p_month -= 1
        if p_month == 0:
            p_month = 13
            p_year -= 1
        p_pos -= 1

    n_pos = pos
    n_year = period.ano
    n_month = period.mes
    while n_pos > 0:
        n_month += 1
        if n_month == 14:
            n_month = 1
            n_year += 1
        n_pos -= 1

    return [f"{p_month:02d}/{p_year:04d}", f"{n_month:02d}/{n_year:04d}"]


def run():
    pos = 15
    first = Periodo.objects.all().first()
    nfirst = first.ano * 100 + first.mes
    last = Periodo.objects.all().last()
    nlast = last.ano * 100 + last.mes
    for pos in range(1, 50):
        control = False
        print(f">>>>>> VALIDATING POS {pos}....", end="")
        for p in Periodo.objects.all():
            pn, vn = next_period(p, pos)
            pp, vp = previous_period(p, pos)
            np = np_periods(p, pos)
            if (vn <= nfirst and pn != np[1]) or (vp >= nlast and pp != np[0]):
                t_n = f"{GREEN}{pn}{NC}" if pn == np[1] else f"{pn}/{RED}{np[1]}{NC}"
                t_p = f"{GREEN}{pp}{NC}" if pp == np[0] else f"{pp}/{RED}{np[0]}{NC}"
                if not control:
                    print("")
                control = True
                print(f"{p} {t_p} {t_n}")
        if not control:
            print(f"{GREEN}OK{NC}")


if __name__ == "__main__":
    run()

# 119044
# 808286
# 712052
# 1077899
# 469194
# 120044
