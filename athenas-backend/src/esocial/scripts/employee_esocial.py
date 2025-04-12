# -.- coding: utf-8 -.-
from datetime import datetime
import django
import os

import codecs

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from rh.models import Servidor
from esocial.models import Event


# set_current_user('athenas')


def evaluate():
    for s in Servidor.objects.active().exclude(
        type_by_possession__in=("VOL", "TCR", "EST", "REX")
    ):
        cad_esocial = (
            Event.objects_all.filter(acronym__in=("s2200", "s2300"))
            .filter(oid=f"{s.matricula}")
            .valids_by_status()
            .count()
        )
        if not cad_esocial:
            print(f"{s.type_by_possession} - {cad_esocial} - {s}")


if __name__ == "__main__":
    evaluate()
