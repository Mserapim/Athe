import datetime

from django.db.transaction import atomic

from contrib.middleware import set_current_user
from rh.gfp.models import Evento, GenreEvent, FolhaModelo, Periodo, FolhaTipo, Folha

from rh.pensao.models import Pensao


def copy_event(origin, genre):
    try:
        new = Evento.objects.get(genre_event=genre, specie_event=origin.specie_event)
    except Evento.DoesNotExist:
        new = origin
        # print(new)
        new.genre_event = genre
        new.pk = None
        new.numero = None
        new.save()
    return new


def copy_config(origin, new):
    # print(origin.automated, origin.calculation)
    new.automated = origin.automated
    new.calculation = origin.calculation
    new.max_quantity = 12
    new.start_validity = datetime.date(2020, 1, 1)
    # new.pk = None
    new.save()
    return new


def create_events(old_events):
    start_number = 104
    news = []
    for old in old_events:
        # criando novo genero
        n_title = f"{old.genre_event.title} 13º"
        new_genre = GenreEvent.objects.get_or_create(
            title=n_title,
            genre_number=start_number,
            type_event=old.genre_event.type_event,
            character=old.genre_event.character,
            config_transparency=old.genre_event.config_transparency,
            socialsecurity_config=old.genre_event.socialsecurity_config,
        )
        new_event = copy_event(old, new_genre[0])
        new_config = copy_config(old.current_config, new_event.current_config)
        news.append(new_event)
        start_number += 1

    return news


def set_new_events(new_events):
    dependents = Evento.objects.filter(
        numero__in=["49800", "90100", "90600", "90900", "91100", "91600", "99100"]
    )
    complement = Evento.objects.get(titulo="COMPLEMENTO VENC. COMISSIONADO 13º")
    for d in dependents:
        without_complement = [
            x if x.numero != complement.numero else None for x in new_events
        ]
        without_complement.remove(None)
        # print(without_complement)
        d.current_config.focuses_on.add(*without_complement)
    urvs = Evento.objects.filter(
        pk__in=[x.pk for x in new_events], titulo__icontains="URV"
    )
    for u in urvs:
        base = Evento.objects.get(titulo=u.titulo.split(" 13º")[0])
        # print(base)
        base_13 = Evento.objects.filter(
            titulo__in=[x.titulo + " 13º" for x in base.current_config.focuses_on.all()]
        )
        # print(base_13)
        if base_13:
            u.current_config.focuses_on.add(*base_13)


def create_payroll_model(new_events):
    pmodel = FolhaModelo.objects.get(slug="gratificacao-natalina")
    pmodel.somente_ativo = True
    pmodel.principais.remove(*pmodel.principais.filter(numero="01500"))
    pmodel.principais.remove(*pmodel.principais.filter(titulo__icontains="URV"))
    pmodel.principais.add(*new_events)
    pmodel.principais.add(Evento.objects.get(numero="07800"))
    pmodel.save()

    return pmodel


def create_period():
    christ_period = Periodo.objects.get_or_create(ano=2020, mes=13)
    return christ_period[0]


def create_payroll_type(payroll_model):
    return FolhaTipo.objects.get(numero="0021")


def resolve_pensions(new_events):
    ne_queryset = Evento.objects.filter(pk__in=[x.pk for x in new_events])
    pensions = Pensao.objects.actives_in().filter(
        events__numero="01500", servidor__ativo=True
    )
    for pension in pensions:
        events_origin = pension.events.filter(
            titulo__in=[ne.titulo.split(" 13º")[0] for ne in ne_queryset]
        )
        # print(events_origin)
        events_2add = ne_queryset.filter(
            titulo__in=[ne.titulo + " 13º" for ne in events_origin]
        )
        # print(events_2add)
        pension.events.add(*events_2add)


def create_payroll(period, payroll_type):
    payroll = Folha.objects.get_or_create(
        periodo=period,
        tipo_folha=payroll_type,
        dt_pagamento=datetime.date(2020, 12, 19),
    )

    return payroll


def main():
    BASE_EVENTS = [
        "00100",
        "00400",
        "00500",
        "00600",
        "00700",
        "00800",
        "01100",
        "01400",
        "02000",
        "04000",
        "06000",
        "06100",
        "06200",
        "06300",
        "06400",
        "06500",
        "71000",
        "05100",
    ]
    # criando eventos
    old_events = Evento.objects.filter(numero__in=BASE_EVENTS)
    with atomic():
        set_current_user(1)
        if old_events:
            news = create_events(old_events)
            # print(Evento.objects.filter(pk__in=[x.pk for x in news], titulo__icontains='URV'))
            set_new_events(news)
            pay_type = create_payroll_type(create_payroll_model(news))
            resolve_pensions(news)
            payroll = create_payroll(create_period(), pay_type)
            print(f"Folha criada {payroll}")
        else:
            print("NAO TEM ESPECIE")
