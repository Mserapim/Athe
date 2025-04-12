# -*- coding: utf-8 -*-
"""
    Este script migra Colaboradores para PossessionCollaborator e PossessionTraine.
    Este script migra Declaração de Atividade para Designação de Exercício.
"""

import django
import os


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()


from contrib.utils import getLogger
from contrib.middleware import set_current_user
from rh.models import MovimentacaoPosse, Servidor


log = getLogger(__name__)


set_current_user("athenas")


def run():
    for employee in Servidor.objects.filter(
        tipo="M", ativo=True
    ):  # , matricula__in=[15997]):
        print(employee)
        # print(f'{employee.my_replacement_substitute().count()} => my_replacement_substitute')
        # print(f'{employee.my_replacement_substitute(owner=True).count()} => my_replacement_substitute owner=True')
        # print(f'{employee.my_replacement_substitute_vacation().count()} => my_replacement_substitute_vacation')
        # print(f'{employee.my_replacement_employee_workplace_vacation().count()} => my_replacement_employee_workplace_vacation')
        # print(f'{employee.my_substitute_employee_vacation().count()} => my_substitute_employee_vacation')
        # print(f'{employee.my_substitute_workplace_vacation().count()} => my_substitute_workplace_vacation')
        print(
            f"{employee.where_replacement_substitute().count()} => where_replacement_substitute"
        )
        print(f"{employee.where_replacement().count()} => where_replacement")
        print(
            f"{employee.get_owner_location_workplace().count()} => get_owner_location_workplace"
        )
        print(
            f"{employee.get_owner_location_workplace_from_workassignment().count()} => get_owner_location_workplace_from_workassignment"
        )
        # print(f'{employee.where_substitute_employee_workplace().count()} => where_substitute_employee_workplace')
        # print(f'{employee.where_substitute_employee().count()} => where_substitute_employee')
        # print(f'{employee.where_replacement_substitute_vacation().count()} => where_replacement_substitute_vacation')
        # print(f'{employee.where_substitute_employee_workplace_vacation().count()} => where_substitute_employee_workplace_vacation')
        # print(f'{employee.where_substitute_employee_vacation().count()} => where_substitute_employee_vacation')
        # print(f'{employee.where_substitute_workplace_vacation().count()} => where_substitute_workplace_vacation')

        # for my_replacement_substitute in employee.my_replacement_substitute():
        #     print(my_replacement_substitute.substitute)
        # for my_replacement_substitute in employee.my_replacement_substitute().values_list('substitute__servidores_lotacao__servidor__matricula', flat=True):
        #     print(my_replacement_substitute)


if __name__ == "__main__":
    run()
