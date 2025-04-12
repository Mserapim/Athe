# -.- coding: utf-8 -.-
import django
import os


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.middleware import set_current_user
from esocial.models import (
    S2200,
    Event,
    S1200,
    PROCESS_STATUS_EVENT_VALIDS_SENT,
    RECTIFICATION,
)
from rh.gfp.models import FolhaEvento
from rh.models import Servidor


set_current_user("gustavodettenborn")


def run():
    # FolhaEvento.objects.filter().update(event_esocial=None)
    # count = 0
    # count_demonstrative_item = 0
    # entries = FolhaEvento.objects.filter(event_esocial__isnull=True).count()
    # query = Event.objects.filter(acronym__in=('s1200', 's1202', 's1207'))
    # total = query.count()
    # for event in query:
    #     try:
    #         count += 1
    #         event = event.event
    #         # print(event)
    #         count_demonstrative_item += event.demonstrative_items.count()
    #         S1200.update_demonstrative_item(event)
    #         # print('---------------------')
    #     except Exception as err:
    #         print(event)
    #         print(err)
    #         print('---------------------')
    #     print(f'count: {count} of {total}')
    # print(f'count {count_demonstrative_item}')
    # print(f'folha evento: {entries} {FolhaEvento.objects.filter(event_esocial__isnull=True).count()}')

    Servidor.objects.filter().update(event_esocial=None)

    # for event in Event.objects.filter(acronym__in=('s2200', 's2300', 's2400', 's2298')):
    #     event = event.event
    #     # print(event)
    #     S2200.update_employee(event)

    query = Event.objects.filter(
        acronym__in=(
            "s1200",
            "s1202",
            "s1207",
            "s1210",
            "s1299",
            "s1298",
            "s5001",
            "s5011",
        )
    )
    total = query.count()
    count = 0
    for event in query:
        event = event.event
        # print(event, event.modified_by_event)
        # print(event.has_exclusion, event.is_invalid)
        # print(event.modified_by_event.process_status, event.modified_by_event.process_status in PROCESS_STATUS_EVENT_VALIDS_SENT)
        # print(event.modified_by_event.action, event.modified_by_event.action == RECTIFICATION)
        # print(event.modified_by_event.group, event.modified_by_event.group == 1)
        event.update_cache()
        event.update_totalizer()
        count += 1
        print(f"{count} of {total}")


if __name__ == "__main__":
    run()
