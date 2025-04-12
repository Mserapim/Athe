# -.- coding: utf-8 -.-
import django
import os
import datetime

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()


from rh.const import ACTIVE, CANCELED
from rh.afastamento.models import BaseLicencaAfastamento


def setup_departure_status_change_date():
    query = BaseLicencaAfastamento.objects.filter().exclude(
        status_change_date__isnull=False
    )
    count = 0
    total = query.count()
    today = datetime.datetime.now().date()
    print(f"{count} of {total}")
    for departure in query.order_by("-data_inicio"):
        status_change_date = None
        if departure.data_fim and departure.data_fim < today:
            status_change_date = departure.data_fim
        elif departure.estado in (ACTIVE, CANCELED):
            status_change_date = departure.data_inicio
        if status_change_date:
            BaseLicencaAfastamento.objects.filter(pk=departure.pk).update(
                status_change_date=status_change_date
            )
        print(f"{count} of {total}")
        count += 1


def run():
    setup_departure_status_change_date()


if __name__ == "__main__":
    run()
