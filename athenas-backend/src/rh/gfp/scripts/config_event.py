# -*- coding: utf-8 -*-

import datetime

from contrib.middleware import set_current_user
from rh.gfp.models import ConfigEvent
from standard.models import ClassCode


def generate():
    set_current_user("athenas")
    start_date = datetime.date(2019, 1, 1)
    event_list = [
        "00100",
        "00400",
        "00500",
        "00600",
        "00700",
        "05100",
        "01100",
        "04000",
    ]
    calculation_list = ClassCode.objects.filter(
        path__startswith="rh.gfp.calcs.remuneration"
    )
    for ev in ConfigEvent.objects.filter(event__numero__in=event_list):
        ConfigEvent(
            start_validity=start_date,
            max_quantity=ev.max_quantity,
            quantity=ev.quantity,
            percentage=ev.percentage,
            base_value=ev.base_value,
            floor=ev.floor,
            ceiling=ev.ceiling,
            automated=ev.automated,
            inverted_calculation=ev.inverted_calculation,
            calculation=calculation_list.get(name_object=ev.calculation.name_object),
            event=ev.event,
            created_at=ev.created_at,
            modified_at=ev.modified_at,
            created_by=ev.created_by,
            modified_by=ev.modified_by,
        ).save()


generate()
