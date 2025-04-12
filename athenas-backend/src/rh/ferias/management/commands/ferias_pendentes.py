# -*- coding: utf-8 -*-

from django.db.models import Count, Sum

from rh.gfp.models import ContraCheque

for cc in ContraCheque.objects.filter(servidor__tipo="M", folha=941, pensioner=None):
    rr = cc.lancamentos.filter(evento__numero__in=["00100", "00500"]).aggregate(
        base=Sum("value"), qtd=Count("value")
    )
    for pas in cc.servidor.periodos_aquisitivos.filter(
        estado=2, periodo_aquisitivo__ano_aquisicao__lt=2018, bloqueado=False
    ):
        print(
            "%s;%s;%d;%d;%d;%d;%d;%0.2f"
            % (
                cc.servidor,
                str(pas.periodo_aquisitivo),
                pas.quantidade_dias,
                pas.dias_usufruidos,
                pas.paid_days,
                pas.dias_agendados,
                pas.quantidade_dias - pas.dias_usufruidos - pas.paid_days,
                min(rr["base"] or 0, 33763),
            )
        )
