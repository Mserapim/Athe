# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from rh.gfp.models import FolhaEvento
from rh.models import Servidor
from django.db.models import Sum

log = getLogger(__name__)


def total_remunerations_efective_by_month():
    events = ["00100", "05100", "49900", "01100", "00500"]
    q_entries = FolhaEvento.objects.order_by("servidor_id").filter(
        servidor__tipo="S",
        folha__periodo__ano__in=[2017, 2018],
        evento__numero__in=events,
        contracheque__pensioner__isnull=True,
    )

    q_employes = q_entries.order_by("servidor").values("servidor").distinct()
    months = [
        (12, 2017),
    ] + [(x, 2018) for x in range(1, 13)]
    for rec in q_employes:
        s = Servidor.objects.get(pk=rec["servidor"])
        if s.is_efetivo:
            print(s)
            for month, year in months:
                print(
                    ":%0.2f"
                    % (
                        q_entries.filter(
                            servidor=s,
                            folha__periodo__mes=month,
                            folha__periodo__ano=year,
                        ).aggregate(t=Sum("correct_value"))["t"]
                        or 0
                    )
                )
            print("")
