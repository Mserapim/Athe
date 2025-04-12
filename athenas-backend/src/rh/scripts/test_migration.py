# -.- coding: utf-8 -.-

import django
import os


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from django.db.models import Q
from rh.models import Servidor

# FIXME: REFACTORY DO TRAINEE


def run():
    for employee in Servidor.objects.filter(
        Q(type_by_possession__in=("EST", "VOL", "TCR", "JCA", "REQ", "RCM", "RFC"))
        | Q(matricula__in=[1047779, 22999, 99310])
    ).filter(ativo=True):
        print(employee)
        print(employee.work_locations_effective_exercise, employee.work_locations)
        print(
            employee.is_trainee(),
            employee.is_voluntary(),
            employee.is_outsourced(),
            employee.is_apprentice(),
            employee.is_ativo(),
            employee.employee_type(),
            employee.requested,
            employee.get_requestmove_at(),
        )

    print(
        f"no_requested_without_onus {Servidor.objects.no_requested_without_onus().count()}"
    )
    print(f"active_requested {Servidor.objects.active_requested().count()}")


if __name__ == "__main__":
    run()
