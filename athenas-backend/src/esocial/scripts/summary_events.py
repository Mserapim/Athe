# -.- coding: utf-8 -.-
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from esocial.const import INCLUSION, MODIFICATION, EXCLUSION, RECTIFICATION
from esocial.models import Event, PROCESS_STATUS_EVENT_NOT_SENT
from django.db.models import Case, Value, When, CharField, Count, F, Q


def summarize():
    events = (
        Event.objects.filter(
            internal=False, process_status__in=PROCESS_STATUS_EVENT_NOT_SENT
        )
        .annotate(
            acronym2=Case(
                When(acronym="s3000"),
                then=Value("modify_event__acronym"),
                default=F("acronym"),
                output_field=CharField(),
            )
        )
        .annotate(
            type_of=Case(
                When(acronym="s3000", then=Value("EXC")),
                When(action=INCLUSION, then=Value("INC")),
                When(action=MODIFICATION, then=Value("MOD")),
                When(action=EXCLUSION, then=Value("EXC")),
                When(action=RECTIFICATION, then=Value("RET")),
                default=F("acronym"),
                output_field=CharField(),
            )
        )
        .values("acronym2")
        .order_by("acronym2", "type_of")
        .annotate(
            INC=Count("pk", filter=Q(type_of="INC")),
            MOD=Count("pk", filter=Q(type_of="MOD")),
            RET=Count("pk", filter=Q(type_of="RET")),
            EXC=Count("pk", filter=Q(type_of="EXC")),
        )
    )

    for e in events:
        print(e)

    return events


if __name__ == "__main__":
    summarize()
