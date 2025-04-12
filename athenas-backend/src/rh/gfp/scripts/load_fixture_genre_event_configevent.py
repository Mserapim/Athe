# -*- coding: utf-8 -*-
"""
    CONFIGURAÇÕES EXCLUSIVAS DE MPTO.

    Este script carrega
        rh/gfp/fixtures/0001_update_genres.json
        rh/gfp/fixtures/0002_update_events.json
        rh/gfp/fixtures/0003_update_configevents.json
"""
import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from django.conf import settings
from django.core.management import call_command

from contrib.middleware import set_current_user
from contrib.utils import getLogger

log = getLogger(__name__)

FIXTURES = (
    "gfp/fixtures/0001_update_genres.json",
    "gfp/fixtures/0002_update_events.json",
    "gfp/fixtures/0003_update_configevents.json",
)


BASE_DIR = getattr(settings, "BASE_DIR", "")

set_current_user("athenas")


def run():
    print("Running forward...")
    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "rh", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


if __name__ == "__main__":
    run()
