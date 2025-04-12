# -*- coding: utf-8 -*-
"""
    Este script criar os servidores beneficiários a partir de uma folha definida.
"""

import os
from datetime import datetime, date

import django
from app.settings import CACHE_PATH

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()


from contrib.daterange import NewDateRange
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from esocial.models import ItemTable
from rh.gfp.models import ContraCheque, Evento, ExtraPaymentPeriod, Periodo
from rh.models import (
    BenefitMovement,
    Publicacao,
    Servidor,
    SocialSecurityConfig,
    SocialSecurityEmployee,
)

log = getLogger(__name__)


set_current_user("athenas")


def task_info(message, type_of=1):
    print(message)


def create_ss_employee(employee):
    print("CRIANDO SEGURIDADE SOCIAL")
    start_validity = datetime(2010, 1, 1).date()
    ss = SocialSecurityConfig.objects.get(pk=3)  # IGEPREV
    sse, created = SocialSecurityEmployee.objects.get_or_create(
        employee=employee, social_security_config=ss, start_validity=start_validity
    )
    print(created, sse)


def close_extra_payment(extra_payment):
    try:
        extra_payment.end_validity = date(2022, 5, 31)
        extra_payment.save()
    except Exception as e:
        print(e)
        message = f"Não foi possivel finalizar a verba {extra_payment}. ERRO: {e}."
        task_info(message, 1)


def create_extra_payment(extra_payment, employee, paycheck=None, pensioner=False):
    try:
        extra_payment_value = extra_payment.value
        if pensioner:
            fe = paycheck.lancamentos.filter(cid=employee.pessoa_fisica.pk).last()
            extra_payment_value = fe.correct_valor

        extra_payment_period = ExtraPaymentPeriod.objects.get_or_create(
            extra_payment=extra_payment.extra_payment,
            employee=employee,
            start_validity=extra_payment.start_validity,
            type_value=extra_payment.type_value,
            value=extra_payment_value,
            main_salary=extra_payment.main_salary,
        )

        message = f"{extra_payment_period} foi criado."
        task_info(message, 1)

    except Exception as e:
        print(e)
        log.exception(e)
        task_info(f"Erro criando verba extra: {e}", 3)


def create_beneficiary_movement(extra_payment, employee, founder_employee=None):
    try:
        benefit = BenefitMovement.objects.get_or_create(
            servidor=employee,
            founder_employee=founder_employee,
            type_legal_representative=3,
            data_posse=extra_payment.start_validity,
            data_exercicio=extra_payment.start_validity,
            financial_effect_date=extra_payment.start_validity,
            benefit_role=ItemTable.objects.get(code="1009", esocial_table=25),
            publicacao_movimentacao=Publicacao.objects.last(),
            texto="benefício",
        )[0]

        message = f"{benefit} foi criado."
        task_info(message, 1)

    except Exception as e:
        print(e)
        benefit = None
        log.exception(e)
        message = f"Erro ao criar a movimentação: {employee}"
        task_info(message, 3)

    return benefit


def create_employee_paycheck(employee, paycheck, period, benefit=None):
    _period = NewDateRange.from_month(period.ano, period.mes)
    termination_date = paycheck.servidor.termination_date
    if (
        termination_date is not None
        and _period.in_range(paycheck.servidor.termination_date) is True
    ):
        return

    new_paycheck, created = ContraCheque.objects.get_or_create(
        servidor=employee,
        folha_id=paycheck.folha_id,
        benefit_number=benefit.benefit_number,
    )
    message = f"{new_paycheck} foi criado."
    task_info(message, 1)

    fe, created, old_fields = new_paycheck.update_or_create_entry(
        False,
        True,
        **{"status": "CT", "evento": Evento.objects.get(id=1816), "automated": True},
    )

    new_paycheck.recalculate(consolidate=1)
    message = f"{new_paycheck} adicionou os seguintes eventos: {fe}"
    task_info(message, 1)


def create_employee_pensioner(pensions, extra_payment, paycheck, period):
    employees = []
    try:
        for pension in pensions:
            print(f"CRIANDO PENSIONISTA: {pension.pensionista}")
            employee = Servidor.objects.get_or_create(
                pessoa_fisica=pension.pensionista, type_by_possession="BFP"
            )[0]
            create_ss_employee(employee)

            benefit = create_beneficiary_movement(
                extra_payment, employee, pension.servidor
            )
            if benefit is not None:
                create_extra_payment(extra_payment, employee, paycheck, pensioner=True)
                create_employee_paycheck(employee, paycheck, period, benefit)

            employees.append(employee)

        close_extra_payment(extra_payment)

    except Exception as e:
        print(e)
        log.exception(e)
        message = f"Erro ao criar o beneficiário do servidor: {pension.servidor}"
        task_info(message, 3)

    return employees


def create_employee_benefit(employee, extra_payment, paycheck, period):
    try:
        type_by_possession = "MAP" if employee.tipo == "M" else "SAP"
        employee = Servidor.objects.get_or_create(
            pessoa_fisica=employee.pessoa_fisica, type_by_possession=type_by_possession
        )[0]
        create_ss_employee(employee)
        benefit = create_beneficiary_movement(extra_payment, employee)
        if benefit is not None:
            create_extra_payment(extra_payment, employee)
            close_extra_payment(extra_payment)
            create_employee_paycheck(employee, paycheck, period, benefit)

    except Exception as e:
        log.exception(e)
        print(e)
        message = f"Erro ao criar o beneficiário: {employee}"
        task_info(message, 3)

    return employee


def delete_paychecks(period):
    delete_query = (
        ContraCheque.objects.filter(
            servidor__ativo=False, folha__periodo=period, folha__complement=0
        )
        .exclude(
            servidor__termination_date__month=period.mes,
            servidor__termination_date__year=period.ano,
        )
        .order_by("folha__periodo")
    )

    for paycheck in delete_query:
        print(f"Excluindo contracheque: {paycheck}")
        paycheck.lancamentos.filter().delete()
        paycheck.delete()


def create_beneficiaries_by_payroll(period):
    PENSION_DEATH = 2
    PASS = 57

    query = ContraCheque.objects.filter(
        servidor__ativo=False,
        folha__periodo=period,
        folha__complement=0,
        pensioner__isnull=True,
    ).order_by("folha__periodo")

    created_beneficiaries = "%s/created_beneficiaries_%s.csv" % (
        CACHE_PATH,
        str(date.today()),
    )
    with open(created_beneficiaries, "w") as file_created_beneficiaries:
        for paycheck in query:
            try:
                extra_payment = (
                    paycheck.servidor.extrapaymentperiods.filter(extra_payment_id=PASS)
                    .order_by("pk")
                    .last()
                )
                pensions = paycheck.servidor.pensao_pagador.filter(
                    data_fim__isnull=True, type_of_pension=PENSION_DEATH
                )

                if pensions:
                    print(f"INSTITUIDOR DA PENSÃO: {paycheck.servidor}\n")
                    file_created_beneficiaries.write(
                        f"INSTITUIDOR DA PENSÃO: {paycheck.servidor}\n"
                    )

                    pensioners = create_employee_pensioner(
                        pensions, extra_payment, paycheck, period
                    )
                    for pensioner in pensioners:
                        file_created_beneficiaries.write(
                            f"---- BENEFICIÁRIO: {pensioner} | {pensioner.type_by_possession}\n"
                        )

                else:
                    print(f"CRIANDO BENEFICIÁRIO: {paycheck.servidor}\n")
                    file_created_beneficiaries.write(
                        f"CRIANDO BENEFICIÁRIO PARA: {paycheck.servidor}\n"
                    )
                    beneficiary = create_employee_benefit(
                        paycheck.servidor, extra_payment, paycheck, period
                    )
                    file_created_beneficiaries.write(
                        f"---- BENEFICIÁRIO: {beneficiary} | {beneficiary.type_by_possession}\n"
                    )

            except Exception as err:
                log.exception(err)
                task_info(f"Erro criando beneficiário: {err}", 3)

    delete_paychecks(period)


def run(period, clear):
    if clear:
        for employee in Servidor.objects.filter(
            type_by_possession__in=("BFP", "MAP", "SAP", "XXX"),
            created_at__gte=datetime(2022, 7, 5).date(),
        ):
            print(
                f"APAGANDO SERVIDOR E CONTRACHEQUE: {employee} | {employee.type_by_possession}"
            )
            employee.paychecks.filter().delete()
            for p in employee.posses.all():
                if hasattr(p, "benefitmovement"):
                    p.benefitmovement.benefit_suspensions.filter().delete()
                p.delete()

            employee.delete()

    create_beneficiaries_by_payroll(period)


if __name__ == "__main__":
    print("#" * 100)
    print("Script de Geração de Beneficiários.")
    print("#" * 100)

    payroll_month = input("Informe um mês: (int): ")

    payroll_year = input("Informe um ano: (int): ")

    clear = bool(
        input(
            "Gostaria de excluir as informações geradas anteriormente? Default: False : "
        )
    )

    period = Periodo.objects.get(mes=payroll_month, ano=payroll_year)
    run(period, clear)
