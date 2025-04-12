# -*- coding: utf-8 -*-

from contrib.middleware import get_current_user
from common.util.api.waitingwork import reg_waiting_work
from engine.mq.models import Task


@reg_waiting_work("get_tasks_on_demand_count")
def get_tasks_on_demand_count():
    count = 0

    try:
        count = Task.objects.filter(
            owner=get_current_user(), state__in=["ready", "failed", "progress"]
        ).count()
    except Exception:
        pass

    return {
        "title": "Relatórios prontos",
        "count": count,
        "type": "relatórios" if count > 1 else "relatório",
        "controller": None,
    }
