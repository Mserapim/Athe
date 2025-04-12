# -*- coding: utf-8 -*-
from rh.gfp.models import FolhaEvento, Evento, ContraCheque
from django.db.models import Count


def duplicateds_unique_entries(payroll=None):
    entries_info = []
    query = FolhaEvento.objects.all()
    if payroll:
        query = query.filter(folha=payroll)
    for fe in (
        query.values(
            "contracheque",
            "evento",
            "info",
            "servidor",
            "reference_year",
            "reference_month",
            "cid",
        )
        .annotate(qtde=Count("contracheque"))
        .filter(qtde__gt=1)
    ):
        cc = ContraCheque.objects.get(pk=fe["contracheque"])
        ev = Evento.objects.get(pk=1258)
        entries_info.append(fe)
        print(fe["qtde"], cc, ev)
    return entries_info


def compare_13_payroll(payroll):
    # f = Folha.objects.filter(pk=1006).first()
    idx = 1
    for cc in f.paychecks.filter(pensioner__isnull=True):
        rem1 = cc.lancamentos.filter(
            evento__numero__in=[
                "10400",
                "10500",
                "10600",
                "10700",
                "10800",
                "10900",
                "11000",
                "11100",
                "11200",
                "11300",
                "11400",
                "11500",
                "11600",
                "11700",
                "11800",
                "11900",
            ]
        ).aggregate(total=Sum("correct_valor"))["total"]
        ev13 = Evento.objects.get(numero="01500")
        calc = ev13.calculation.cls(cc.servidor, cc.folha, ev13)
        value = round(calc.value(), 2)
        if abs(round(float(rem1 or 0), 2) - value) > 0.019:
            print(f"{idx:04d} {rem1} != {value} {cc}")
            idx += 1


# c = 1
# for fe in f.lancamentos.filter(prazo=999, evento__numero='53600'):
#     print(f'{c:03d} {fe.parcela}/{fe.prazo} {fe.servidor.matricula} {fe}')
#     c += 1
