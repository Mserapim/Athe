# -*- coding: utf-8 -*-

from rh.gfp.models import Evento
from django.db.models import Max
from contrib.middleware import set_current_user

set_current_user("athenas")

Evento.objects.update(order=1)
events = [ev.numero for ev in Evento.objects.filter(genre_event__isnull=False)]
events_loops = {}
while events:
    iev = events.pop(0)
    ev = Evento.objects.get(numero=iev)
    print(ev)
    if (
        ev.current_config
        and ev.current_config.automated
        and ev.current_config.focuses_on.exists()
    ):
        if ev.current_config.focuses_on.filter(numero__in=events).exists():
            events.append(iev)  # Send to end of list
            if iev not in events_loops:
                events_loops[iev] = 0
            events_loops[iev] += 1
            print("SENDO TO END %d" % events_loops[iev])
            if events_loops[iev] > 1:
                print(
                    [
                        ev1.numero
                        for ev1 in ev.current_config.focuses_on.filter(
                            numero__in=events
                        )
                    ]
                )
            else:
                print("")
            if events_loops[iev] > 100:
                print("LOOP %s %d" % (iev, events_loops[iev]))
                break
        else:
            # Updating order of event
            order = (
                ev.current_config.focuses_on.aggregate(max_order=Max("order"))[
                    "max_order"
                ]
                + 1
            )
            ev.order = order
            ev.save()
            print("POP *")
    else:
        print("POP")
