# -*- coding: utf-8 -*-
"""
    Cria exposição a risco para RGPS.
"""

import django
import os
import datetime

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

RED = "\033[0;31m"
GREEN = "\033[0;32m"
ORANGE = "\033[0;33m"
WHITE = "\033[1;37m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color

CALENDAR_YEAR = 2022


def run():
    from contrib.middleware import set_current_user
    from esocial.models import Configuration
    from rh.models import Lotacao, PessoaFisica, SocialSecurityEmployee, Servidor
    from health.sst.models import (
        EnvironmentWorkingCondition,
        EnvironmentHarmfulAgent,
        HarmfulAgent,
        ExposureEmployeeEnvironment,
    )

    set_current_user("fredericofrota")
    start_validity = datetime.datetime(2023, 1, 1).date()
    # configuration = Configuration.current_config()

    def _create_environment_working_condition():
        return EnvironmentWorkingCondition.objects.update_or_create(
            start_validity=start_validity,
            workplace=Lotacao.objects.get(pk=454),
            responsible=PessoaFisica.objects.get(pk=1961),
            description_departament=f"{Lotacao.objects.get(pk=454)}",
        )[0]

    def _create_environment_harmful_agent(environment_working_condition):
        return EnvironmentHarmfulAgent.objects.update_or_create(
            environment_working_condition=environment_working_condition,
            harmful_agent=HarmfulAgent.objects.get(code="09.01.001"),
        )[0]

    def _create_exposure_employee_environment(environment_working_condition, employee):
        print(environment_working_condition)
        print(employee)
        return ExposureEmployeeEnvironment.objects.update_or_create(
            start_validity=(
                start_validity
                if start_validity > employee.exercise_date
                else employee.exercise_date
            ),
            employee=employee,
            environment_working_condition=environment_working_condition,
            description_activity="ATIVIDADE MINISTERIAL",
        )[0]

    environment_working_condition = _create_environment_working_condition()
    print(f"{environment_working_condition} {GREEN}OK{NC}")
    environment_harmful_agent = _create_environment_harmful_agent(
        environment_working_condition
    )
    print(f"{environment_harmful_agent} {GREEN}OK{NC}")

    start_date = datetime.datetime.today()

    for sse in (
        SocialSecurityEmployee.objects.by_regime(1)
        .exclude(employee__type_by_possession__in=("EST", "VOL", "TCR", "JCA", "COE"))
        .order_by("employee")
    ):
        if (
            Servidor.objects.filter(pk=sse.employee.pk)
            .active_in(start_date=start_date)
            .exists()
        ):
            add = f"{GREEN}OK{NC}"
            _create_exposure_employee_environment(
                environment_working_condition, sse.employee
            )
            print(f"{sse.employee} {add}")
            # configuration.employee_filter.add(sse.employee)


if __name__ == "__main__":
    run()
