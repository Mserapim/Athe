# -.- coding: utf-8 -.-
import os
import codecs
import django


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from rh.gfp.models import *
from contrib.middleware import set_current_user
from esocial.models import S1010, ItemTable
from contrib.utils import getLogger
from rh.gfp.models import Evento
from django.db.models import Count
from django.conf import settings


log = getLogger(__name__)


set_current_user("athenas")


def base_event(inst):
    if inst.genre_event:
        rs = Evento.objects.filter(
            genre_event__genre_number=inst.genre_event.genre_number,
            specie_event__specie_number="00",
        )
        # print(f'inst {inst}')
        # print(f'rs {rs}')
        if rs:
            return rs.first()
    return inst


def test(instance_outside, event):
    focuses_on_monthly_cp = instance_outside.aplica_em.filter(
        event__carater__in=[
            8,  # previdenciario
            17,  # previdenciario 13
            # 18,  # previdenciario Férias
            19,  # previdenciario RRA
        ],
        event__tags__label="rgps",
    )
    if focuses_on_monthly_cp.count() > 0:
        print(focuses_on_monthly_cp.count(), event)


def run():
    for e in Evento.objects.filter():
        # print(f'=> {e}')
        instance_outside = base_event(e)
        test(instance_outside, e)


if __name__ == "__main__":
    run()
