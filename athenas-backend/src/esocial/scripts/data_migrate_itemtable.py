# -.- coding: utf-8 -.-
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from django.conf import settings
from django.core.management import call_command

FIXTURES = ("fixtures/initialdb_0004_itemtable.json",)


def load_fixture(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running initial data...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "esocial", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


if __name__ == "__main__":
    load_fixture()
