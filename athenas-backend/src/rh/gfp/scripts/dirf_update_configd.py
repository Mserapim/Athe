# -*- coding: utf-8 -*-
"""
    RRA UPDATE.
"""

import django
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'app.settings'
django.setup()

RED = '\033[0;31m'
GREEN = '\033[0;32m'
ORANGE = '\033[0;33m'
WHITE = '\033[1;37m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

CALENDAR_YEAR = 2022


def run():

    from rh.gfp.models import Evento
    from rh.gfp.dirf.models import Token
    from django.db.models import Count, Q

    for ev in Evento.objects.exclude(
            carater__in=[6, 7]).annotate(
            entries=Count('lancamentos', filter=Q(lancamentos__folha__dt_pagamento__year=CALENDAR_YEAR))).exclude(
            entries=0).annotate(
            dirf_tokens=Count('as_token', filter=Q(as_token__dialect__calendar_year=CALENDAR_YEAR)))  # .filter(dirf_tokens=0):
        add = ''
        q_tokens = set([t for t in Token.objects.filter(dialect__calendar_year=CALENDAR_YEAR, eventos__genre_event=ev.genre_event)])
        tokens = ", ".join([str(t) for t in q_tokens]) if q_tokens else ""
        if len(q_tokens) > 0:
            for token in q_tokens:
                # token = q_tokens.pop()
                token.eventos.add(ev)
                add = f'{GREEN}OK{NC}'
        print(f'{ev.dirf_tokens:03d} {ev.carater} {ev} {ORANGE}{tokens}{NC} {add}')


if __name__ == "__main__":
    run()
