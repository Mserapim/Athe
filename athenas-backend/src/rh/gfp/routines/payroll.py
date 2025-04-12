# -*- coding: utf-8 -*-

from contrib.utils import getLogger

log = getLogger("rh.gfp.loaders")


def update_acountplan(year, add=False):
    from rh.gfp.planoconta.models import Plano

    for p in Plano.objects.filter(ano_calendario=year):
        for e in p.eventos.all():
            if e.genre_event not in p.genre_events.all() and e.genre_event:
                print(p, e.genre_event.genre_number, p.genre_events.add(e.genre_event))

    for p in Plano.objects.filter(ano_calendario=year).order_by(
        "folha_tipo", "tipo", "titulo"
    ):
        for ge in p.genre_events.all():
            events = [e.pk for e in p.eventos.all()]
            adds = [ev for ev in ge.events.exclude(pk__in=events)]
            if adds:
                print(p.folha_tipo, p.get_tipo_display(), p)
                if add:
                    for ev in adds:
                        p.eventos.add(ev)
                        print(ev.numero)
                print("")


def verify_entries_plans(payroll, type_of=2):
    from rh.gfp.planoconta.models import PlanoConta

    events = []
    for fe in payroll.lancamentos.order_by("servidor", "evento__numero"):
        plans = fe.evento.em_plano.filter(
            folha_tipo=payroll.tipo_folha,
            ano_calendario=payroll.periodo.ano,
            tipo=type_of,
        )
        ssc = fe.servidor.get_socialsecurity_by_validity(range=fe.folha.date_range)
        regime_social_security = ssc.regime if ssc else None
        acountplans = PlanoConta.objects.filter(
            plano__in=plans,
            tipo=1,
            finalidade=1,
            regime_previdenciario=regime_social_security,
        )
        if acountplans.count() > 1 and fe.evento not in events:
            events.append(fe.evento)
            print(
                fe.evento, [(ap.plano, ap.regime_previdenciario) for ap in acountplans]
            )


def validate_nl(payroll, finalidade=2):
    from rh.gfp.planoconta.models import PlanoConta

    events = []
    total = 0.0
    nl = {}
    for fe in payroll.lancamentos.filter(status__in=("CT", "CE")).order_by(
        "servidor", "evento__numero"
    ):
        plans = fe.evento.em_plano.filter(
            folha_tipo=payroll.tipo_folha,
            ano_calendario=payroll.periodo.ano,
            tipo__in=[1, 2, 3],
        )
        ssc = fe.servidor.get_socialsecurity_by_validity(range=fe.folha.date_range)
        regime_social_security = ssc.regime if ssc else None
        acountplans = PlanoConta.objects.filter(
            plano__in=plans,
            tipo=1,
            finalidade=finalidade,
            regime_previdenciario=regime_social_security,
        )
        if acountplans.count() > 1 and fe.evento not in events:
            events.append(fe.evento)
            print(
                fe.evento, [(ap.plano, ap.regime_previdenciario) for ap in acountplans]
            )
        elif acountplans.count() == 0 and fe.evento not in events:
            events.append(fe.evento)
            print("NOT CONFIGURED: %s" % fe.evento)
        for ap in acountplans:
            value = float(
                fe.employer_contribution if ap.plano.tipo == 3 else fe.value
            )  # TIPO=PATRONAL
            value *= -1 if ap.plano.tipo == 1 else 1  # TIPO=CONSIGNACAO
            value *= -1 if ap.plano.invert_negative else 1  # INVERT_NEGATIVE = True
            total += value
            if ap.plano.tipo not in nl:
                nl[ap.plano.tipo] = {}
            if ap.regime_previdenciario not in nl[ap.plano.tipo]:
                nl[ap.plano.tipo][ap.regime_previdenciario] = {}
            if ap not in nl[ap.plano.tipo][ap.regime_previdenciario]:
                nl[ap.plano.tipo][ap.regime_previdenciario][ap] = {"value": 0.0}
            nl[ap.plano.tipo][ap.regime_previdenciario][ap]["value"] += value
            # print '%12.2f %12.2f' % (value, total)

    return round(total, 2), nl


def validate_resumo_geral(payroll):
    from django.db.models import Sum

    p = payroll.lancamentos.filter(
        evento__carater__in=[1, 2, 3, 9, 13, 15, 21]
    ).aggregate(total=Sum("value"), contribution=Sum("employer_contribution"))
    d = payroll.lancamentos.filter(evento__carater__in=[4, 5, 6, 7, 16, 20]).aggregate(
        total=Sum("value"), contribution=Sum("employer_contribution")
    )
    t = payroll.lancamentos.aggregate(
        total=Sum("value"), contribution=Sum("employer_contribution")
    )

    if p["total"] + d["total"] != t["total"]:
        print("ERROR in values")
        return None
    else:
        return p["total"] + t["contribution"]


def validate_paychecks(payroll):
    # VALIDATING PENSIONS
    for pc in payroll.paychecks.all():
        pass


def clear_accountplan(year, exclude_events=False):
    from rh.gfp.planoconta.models import Plano

    for p in Plano.objects.filter(ano_calendario=year):
        print(">>>> %s" % p)
        if exclude_events:
            for ev in p.eventos.filter(genre_event=None):
                print(ev, p.eventos.remove(ev))
        for pc in p.contas.exclude(tipo=1):
            print(pc, p.contas.remove(pc))
        if not p.eventos.exists() or p.tipo not in [1, 2, 3]:
            p.delete()
