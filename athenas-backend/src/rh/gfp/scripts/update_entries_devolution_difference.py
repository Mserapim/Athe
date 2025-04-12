# -*- coding: utf-8 -*-
"""
    Este script configura os eventos das bases de rgps e rpps aplicando:
        esocial_cp = '00'
        esocial_cprp = '00'
        esocial_irrf = '9'
"""

import os
import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from esocial.models import ItemTable
from rh.gfp.models import ConfigEvent, GenreEvent
from contrib.middleware import set_current_user


set_current_user("athenas")


def update_entries():
    print(
        """
    Este script configura os eventos de rgps e rpps que não são espécie 00 aplicando:
        esocial_cp = '00'
        esocial_cprp = '00'
        esocial_irrf = '9'
"""
    )

    events = [
        ge
        for ge in GenreEvent.objects.filter(
            events__tags__label__in=("rgps", "rpps", "irrf")
        )
    ]

    esocial_cp = ItemTable.objects.get(code="00", esocial_table="98")
    esocial_cprp = ItemTable.objects.get(code="00", esocial_table="96")
    esocial_irrf = ItemTable.objects.get(code="9", esocial_table="21")

    for ce in ConfigEvent.objects.filter(
        event__genre_event__in=events, event__tipo="P"
    ).exclude(event__specie_event__specie_number="00"):
        ConfigEvent.objects.filter(pk=ce.pk).update(
            esocial_cp=esocial_cp, esocial_cprp=esocial_cprp, esocial_irrf=esocial_irrf
        )
        print(ce)
        # print(f'esocial_cp de {ce.esocial_cp.code} para {esocial_cp.code}\nesocial_cprp de {ce.esocial_cprp.code} para {esocial_cprp.code}\nesocial_irrf de {ce.esocial_irrf.code} para {esocial_irrf.code}')


if __name__ == "__main__":
    update_entries()
