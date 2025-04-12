# -*- coding: utf-8 -*-
"""
    Este script migra Dados de Trainee para PossessionTraine.
"""

import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.models import PossessionTrainee, Trainee, DeclaracaoAtividade

log = getLogger(__name__)


set_current_user("athenas")


def run():
    print("""Este script migra Dados de Trainee para PossessionTraine.""")

    def _possession_migrate(employee):
        log.debug(f"{employee.type_by_possession} | {employee}")
        try:
            possession = PossessionTrainee.objects.get(servidor=employee)
            publicacao_movimentacao = possession.publicacao_movimentacao

            activities = DeclaracaoAtividade.objects.filter(servidor=employee)

            if activities.exists():
                act = activities.filter(data_exercicio=possession.data_exercicio).last()
                if act.publicacao_movimentacao:
                    publicacao_movimentacao = act.publicacao_movimentacao

            change = [
                possession.employee_supervisor != employee.employee_supervisor
                or possession.educational_institution
                != employee.educational_institution
                or possession.integration_agent != employee.integration_agent
                or possession.nature != employee.nature
                or possession.level != employee.level
                or possession.occupation_area != employee.occupation_area
                or possession.insurance_number != employee.insurance_number
                or possession.value != employee.value
                or possession.publicacao_movimentacao != publicacao_movimentacao
            ]

            if True in change:
                print(f"{employee.type_by_possession} | {employee}")
                PossessionTrainee.objects.filter(pk=possession.pk).update(
                    publicacao_movimentacao=publicacao_movimentacao,
                    employee_supervisor=employee.employee_supervisor,
                    educational_institution=employee.educational_institution,
                    integration_agent=employee.integration_agent,
                    nature=employee.nature,
                    level=employee.level,
                    occupation_area=employee.occupation_area,
                    insurance_number=employee.insurance_number,
                    value=employee.value,
                )
        except Exception as err:
            print(err)
            print(employee, employee.type_by_possession)

    for employee in Trainee.objects.filter():
        _possession_migrate(employee)


if __name__ == "__main__":
    run()
