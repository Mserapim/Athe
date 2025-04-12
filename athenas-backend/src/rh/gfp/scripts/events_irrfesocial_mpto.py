# -*- coding: utf-8 -*-
"""
    Configurando eventos do MPTO para tag irrf-esocial.
"""

import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()


def run():
    from rh.gfp.models import Evento
    from standard.models import Choice
    from contrib.middleware import set_current_user

    set_current_user("athenas")

    events = (
        "99100",
        "99101",
        "99106",
        "99200",
        "99201",
        "99206",
        "99900",
        "99901",
        "99906",
        "99907",
    )
    tag = Choice.objects.get(label="irrf-esocial")
    for e in Evento.objects.filter(numero__in=events):
        print(f"Adicionando {tag} à {e.numero}")
        e.tags.add(tag)


if __name__ == "__main__":
    run()
