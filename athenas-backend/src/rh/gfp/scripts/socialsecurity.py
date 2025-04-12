# -*- coding: utf-8 -*-

# from django.db import models

from contrib.middleware import set_current_user
from rh.gfp.models import Previdencia
from rh.models import SocialSecurity
from django.db import models

set_current_user("raysonsilva")

for p in Previdencia.objects.order_by(
    "pessoa_juridica", "regime_previdenciario", "data_vigencia"
):
    result = p.faixas.aggregate(
        avg=models.Avg("pct_patronal"), max=models.Max("pct_patronal")
    )
    percentage_of_employer = 0
    if result["max"] == result["avg"] and result["max"]:
        percentage_of_employer = result["max"]
    print(
        f"{p.get_regime_previdenciario_display()} {p.get_identifier_display()} {p.data_vigencia} {p}",
        end="",
    )
    ss, created = SocialSecurity.objects.get_or_create(
        legal_person=p.pessoa_juridica,
        identifier=p.identifier,
        start_validity=p.data_vigencia,
        publication=p.publicacao,
        socialsecurity_regime=p.regime_previdenciario,
        percentage_of_employer=percentage_of_employer,
    )
    for f in p.faixas.all():
        ssr, createdr = ss.ranges.get_or_create(
            socialsecurity=ss,
            lower_limite=f.limite_inferior,
            upper_limite=f.limite_superior,
            percentage=f.pct,
            reducer=f.reducer,
        )
    print(f' {"OK" if created else "**"}')
