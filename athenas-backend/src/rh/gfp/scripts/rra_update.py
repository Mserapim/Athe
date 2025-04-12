# -*- coding: utf-8 -*-
"""
    RRA UPDATE.
"""

import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

events_to_update = (
    "00401",
    "01501",
    "01502",
    "01701",
    "02002",
    "02006",
    "04801",
    "05001",
    "05002",
    "06302",
    "10501",
    "11802",
    "90001",
    "90101",
    "90501",
    "90506",
    "90601",
    "91501",
)

irrf_rra_to_update = ("99200",)


def copy_events(source, target):
    for ev in source.eventos.all():
        if ev not in target.eventos.all():
            target.eventos.add(ev)

    print(f"{source}: {source.eventos.count()} {target}: {target.eventos.count()}")
    if target.eventos.count() > source.eventos.count():
        for ev in target.eventos.all():
            if ev not in source.eventos.all():
                print(ev)


def update_irrf():
    from rh.gfp.models import Evento, FolhaEvento
    from rh.gfp.dirf.models import Token
    from django.db.models import Count, Q

    q_irrf = FolhaEvento.objects.filter(
        rra_employee__isnull=True, evento__numero__in=irrf_rra_to_update
    )

    for irrf in q_irrf:
        q_rra_employees = (
            irrf.contracheque.lancamentos.filter(rra_employee__isnull=False)
            .order_by("rra_employee")
            .values("rra_employee")
            .distinct()
        )
        if q_rra_employees.count() == 1:
            print(f"Atualizando {irrf.contracheque} > {q_rra_employees}")
            irrf.contracheque.lancamentos.filter(pk=irrf.pk).update(
                rra_employee=q_rra_employees[0]["rra_employee"]
            )
        else:
            print(f"ERRO com IRRF RRA: {irrf.contracheque} {q_rra_employees}")

    # Copiando eventos dos tokens
    tokens = Token.objects.get(
        dialect__calendar_year=2022, slug="rendimentos-tributaveis"
    )
    tokent = Token.objects.get(
        dialect__calendar_year=2022, slug="rra-rendimentos-tributaveis"
    )
    copy_events(tokens, tokent)
    tokens = Token.objects.get(dialect__calendar_year=2022, slug="previdencia-social")
    tokent = Token.objects.get(
        dialect__calendar_year=2022, slug="rra-previdencia-social"
    )
    copy_events(tokens, tokent)
    tokens = Token.objects.get(
        dialect__calendar_year=2022, slug="rendimentos-tributaveis"
    )
    tokent = Token.objects.get(dialect__calendar_year=2022, slug="rra-quantidade-meses")
    copy_events(tokens, tokent)

    for ev in Evento.objects.annotate(
        rra_count=Count(
            "lancamentos", filter=Q(lancamentos__rra_employee__isnull=False)
        ),
        tokens=Count(
            "as_token",
            filter=Q(
                as_token__slug__startswith="rra-", as_token__dialect__calendar_year=2022
            ),
        ),
    ).filter(rra_count__gt=0, tokens=0):

        print(ev)


def run():
    from rh.gfp.models import ContraCheque, FolhaEvento, Folha, RRAEmployee, RRA

    sheet = Folha.objects.get(pk=1125)
    rra = RRA.objects.get(pk=38)
    for paycheck in ContraCheque.objects.filter(folha=sheet):
        rra_employee = RRAEmployee.objects.filter(
            employee=paycheck.servidor, rra=rra
        ).last()
        if rra_employee:
            print(paycheck)
            print(rra_employee)
            for entry in paycheck.lancamentos.filter(
                evento__numero__in=events_to_update, rra_employee__isnull=True
            ).exclude(reference_year=2022):
                print(entry.reference_year, entry)
                FolhaEvento.objects.filter(pk=entry.pk).update(
                    rra_employee=rra_employee, count_as_previous_exercise=True
                )
            qtd = (
                paycheck.lancamentos.filter(
                    rra_employee__isnull=False, evento__numero__in=events_to_update
                )
                .order_by("reference_month", "reference_year")
                .values("reference_month", "reference_year")
                .distinct()
                .count()
            )

            idx = 1
            for k in (
                paycheck.lancamentos.filter(
                    rra_employee__isnull=False, evento__numero__in=events_to_update
                )
                .order_by("reference_month", "reference_year")
                .values("reference_month", "reference_year")
                .distinct()
            ):
                print(
                    idx,
                    k,
                    set(
                        [
                            fe.evento.numero
                            for fe in paycheck.lancamentos.filter(
                                reference_year=k["reference_year"],
                                reference_month=k["reference_month"],
                                evento__numero__in=events_to_update,
                            ).order_by("evento__numero")
                        ]
                    ),
                )
                idx += 1

            print(f"RRAEmployee.months: {rra_employee.months} | {qtd} | {(idx -1 )}")
            RRAEmployee.objects.filter(pk=rra_employee.pk).update(months=qtd)
            print("------------------")


if __name__ == "__main__":
    run()
