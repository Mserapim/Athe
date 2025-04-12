# -*- coding: utf-8 -*-
from common.util.api.waitingwork import reg_waiting_work


@reg_waiting_work("workerreminder_pending")
def workerreminder_unresolved():
    from judicial.models import WorkerReminder
    from contrib.utils import employee_from_user
    from contrib.middleware import get_current_user
    from django.db.models import Q

    employee = employee_from_user(get_current_user())
    count = 0

    if employee:
        query = Q(
            Q(part__lawsuit__location__in=employee.work_locations)
            & Q(receiver=employee)
            & Q(resolved=False)
        )

        try:
            count = WorkerReminder.objects.filter(query).count()

        except AttributeError:
            count = 0

    return {
        "title": "Pré-análise",
        "count": count,
        "type": "documentos" if count > 1 else "documento",
        "controller": "EJudManage",
    }
