# -*- coding: utf-8 -*-
from datetime import date
from rh.models import Servidor
from rh.gfp.models import ExtraPayment


extra_payments_01300 = [
    [80, "01300", "5297,62"],
    [77, "01300", "6519,67"],
    [76, "01300", "5961,84"],
    [40, "01300", "3400,51"],
    [36, "01300", "3683,6"],
    [27, "01300", "827,95"],
    [58, "01300", "4874,73"],
    [56, "01300", "1984,06"],
    [31, "01300", "2428,07"],
]

ep = ExtraPayment.objects.filter(slug__icontains="VANTAGEM_ART37XV").first()
if ep:
    for epp13 in extra_payments_01300:
        print(f"{epp13[0]} {epp13[2]} ", end="")
        obj, created = ep.periods.get_or_create(
            employee=Servidor.objects.get(matricula=epp13[0]),
            defaults={
                "value": epp13[2].replace(",", "."),
                "start_validity": (date(2021, 1, 1)),
            },
        )
        print("OK" if created else "OK*")
