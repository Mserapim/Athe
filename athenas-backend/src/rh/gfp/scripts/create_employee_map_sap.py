# -*- coding: utf-8 -*-
"""
    Este script corrige as publicações de movimentação dos colaboradores.
    Escrevendo as publicações que estão em DeclaracaoAtividade para PossessionCollaborator.
"""

import os
from datetime import datetime

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()


from contrib.daterange import NewDateRange
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from esocial.models import ItemTable
from rh.gfp.models import ContraCheque, ExtraPayment, Folha
from rh.models import (
    BenefitMovement,
    Publicacao,
    Servidor,
    SocialSecurityConfig,
    SocialSecurityEmployee,
)
from django.db.models import Case, IntegerField, Count, F, Q, Value, When, Min

log = getLogger(__name__)


set_current_user("athenas")


def task_info(message, type_of=1):
    print(message)


def create_beneficiary_paycheck(paycheck, inc_progress=0.0):
    try:
        start_date = NewDateRange.from_month(
            paycheck.folha.periodo.ano, paycheck.folha.periodo.mes
        ).first
        type_by_possession = "MAP" if paycheck.servidor.tipo == "M" else "SAP"
        employee = Servidor.objects.get_or_create(
            pessoa_fisica=paycheck.servidor.pessoa_fisica,
            type_by_possession=type_by_possession,
        )[0]

        create_ss_employee(employee)

        print(f"CRIANDO SERVIDOR: {employee} | {type_by_possession}")
        benefit = BenefitMovement.objects.get_or_create(
            servidor=employee,
            data_exercicio=start_date,
            financial_effect_date=start_date,
            benefit_role=ItemTable.objects.get(code="1009", esocial_table=25),
            publicacao_movimentacao=Publicacao.objects.last(),
            texto="benefício",
        )[0]

        paycheck_new, created = ContraCheque.objects.get_or_create(
            servidor=employee,
            folha=paycheck.folha,
            benefit_number=benefit.benefit_number,
        )

        message = f"{paycheck_new} adicionou os seguintes eventos: "
        for entry in paycheck.lancamentos.all():
            fe, created, old_fields = paycheck_new.update_or_create_entry(
                False,
                True,
                **{
                    "status": "CT",
                    # 'cid': mf.pk,
                    "evento": entry.evento,
                    # 'info': f'{mf.participante.solicitacao.codigo}',
                    "valor": entry.valor,
                    "automated": False,
                },
            )
            message += f"\n{entry} => {entry.valor}"

        paycheck.lancamentos.all().delete()
        paycheck.delete()

        task_info(message, 1)

    except Exception as err:
        log.exception(err)
        message = f"{employee} não possui servidor. {err}"
        task_info(message, 3)


def import_beneficiaries_payroll():
    query = ContraCheque.objects.filter(servidor__ativo=False, folha__pk=1057).order_by(
        "folha__periodo"
    )

    total = query.count()
    inc_progress = 100.0 / total if total else 100.0

    for cc in query:
        payroll = cc.folha

        if payroll.status in (3, 4):
            payroll.status = 1

        try:
            create_beneficiary_paycheck(cc, inc_progress=inc_progress)
        except Exception as err:
            log.exception(err)
            print(err)
            task_info(f"Erro criando contracheque: {err}", 3)

    payroll = Folha.objects.get(pk=1061)  # FOLHA 6/2022
    payroll.consolidate_payroll(control_by_lock=False)
    payroll.status = 4
    payroll.save()


def create_ss_employee(employee):
    print("CRIANDO SEGURIDADE SOCIAL")
    start_validity = datetime(2010, 1, 1).date()
    ss = SocialSecurityConfig.objects.get(pk=3)  # IGEPREV
    sse, created = SocialSecurityEmployee.objects.get_or_create(
        employee=employee, social_security_config=ss, start_validity=start_validity
    )
    print(created, sse)


def update_paychecks_map_sap():
    ep = ExtraPayment.objects.get(name="PASS")
    for s in Servidor.objects.filter(type_by_possession__in=("MAP", "SAP")):
        do_process = ""
        paychecks = (
            ContraCheque.objects.exclude(servidor=s)
            .filter(servidor__pessoa_fisica=s.pessoa_fisica)
            .annotate(
                entries=Case(
                    When(
                        ~Q(lancamentos__evento__genre_event__genre_number="094"),
                        then=Count("lancamentos__pk"),
                    ),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            .annotate(
                entries094=Case(
                    When(
                        Q(lancamentos__evento__genre_event__genre_number="094"),
                        then=Count("lancamentos__pk"),
                    ),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            .filter(entries=0, entries094__gt=0)
        )
        qtd_paychecks = paychecks.count()
        if qtd_paychecks:
            min_dt = paychecks.aggregate(dt=Min("folha__dt_pagamento"))["dt"]
            print(
                f"# {s.type_by_possession} - {s} {qtd_paychecks}/{min_dt} {s.exercise_date}"
            )
            for epp in ep.periods.filter(employee__pessoa_fisica=s.pessoa_fisica):
                print(f"> {epp}")
            for cc in paychecks:
                print(f">> {cc}: {[e.evento.numero for e in cc.lancamentos.all()]}")
            do_process = input("Processar servidor? [N/y]")
            if do_process.lower() == "y":
                for cc in paychecks:
                    cc.lancamentos.update(servidor=s)
                paychecks.update(servidor=s)
                ep.periods.filter(employee=s).delete()
                ep.periods.filter(employee__pessoa_fisica=s.pessoa_fisica).update(
                    employee=s
                )
                eepl = (
                    ep.periods.filter(employee__pessoa_fisica=s.pessoa_fisica)
                    .order_by("start_validity")
                    .last()
                )
                if eepl:
                    ep.periods.filter(employee=s, pk=eepl.pk).update(end_validity=None)

                print(do_process, s)


def run():

    # for employee in Servidor.objects.filter(type_by_possession__in=('MAP', 'SAP', 'XXX'), created_at__gte=datetime(2022, 6, 15).date()):
    #     print(f'APAGANDO SERVIDOR E CONTRACHEQUE: {employee} | {employee.type_by_possession}')
    #     employee.paychecks.filter().delete()
    #     for p in employee.posses.all():
    #         if hasattr(p, 'benefitmovement'):
    #             p.benefitmovement.benefit_suspensions.filter().delete()
    #         p.delete()
    #     employee.delete()

    # import_beneficiaries_payroll()
    update_paychecks_map_sap()


if __name__ == "__main__":
    run()
