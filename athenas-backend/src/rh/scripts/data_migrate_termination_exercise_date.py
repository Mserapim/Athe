# -*- coding: utf-8 -*-
"""
    Este script atualiza os campos Servidor.termination_date e Servidor.exercise_date.
    Este script atualiza o campo Acidente de Trânsito de todas Licenças de Saúde.
"""

import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()


from rh.models import Servidor
from rh.afastamento.models import LicencaSaude
from contrib.middleware import set_current_user


def update_acidente_transito():
    rs = input(
        f"\nVocê deseja atualizar o campo Acidente de Trânsito de todas Licenças de Saúde ? (y/N)\n"
    )
    if rs == "y":
        print(
            f"Licenças atualizadas: {LicencaSaude.objects.filter().update(acidente_transito=None)}"
        )


def update_termination_date_exercise_date():
    print(
        "Este script atualiza os campos Servidor.termination_date e Servidor.exercise_date."
    )
    set_current_user("athenas")
    updated = 0
    employees = Servidor.objects.filter()
    total = employees.count()
    print(f"Servidores : {total}")
    for employee in employees:
        employee.exercise_date = employee.data_exercicio
        employee.termination_date = employee.dismissal_date
        Servidor.objects.filter(pk=employee.pk).update(
            exercise_date=employee.exercise_date,
            termination_date=employee.termination_date,
        )
        updated += 1
        print(f"Servidor UPDATED:  {updated} -> {total} | {employee}")
    print(f"Servidor UPDATED:  {updated} -> {total} | {employee}")


if __name__ == "__main__":
    update_acidente_transito()
    update_termination_date_exercise_date()
