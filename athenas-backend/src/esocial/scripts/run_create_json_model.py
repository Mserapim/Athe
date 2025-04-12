# -.- coding: utf-8 -.-
import django
import os
import fnmatch
from django.conf import settings

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.middleware import set_current_user
from esocial.managers.file_support import csv_to_json, create_django_model_by_json_model

DIRECTORY_DATA = "%s/esocial/data/generated" % settings.BASE_DIR
DIRECTORY_DATA_CSV = "%s/csv" % DIRECTORY_DATA

ACRONYMS = []
for root, dirnames, filenames in os.walk("%s" % DIRECTORY_DATA_CSV):
    for filename in fnmatch.filter(filenames, "*.csv"):
        prefix = filename.split(".")[0]
        ACRONYMS.append(prefix.replace("-", "").lower())


set_current_user("rsnascimento")


def run():
    csv_to_json(acronyms=ACRONYMS)
    create_django_model_by_json_model(acronyms=ACRONYMS)


if __name__ == "__main__":
    run()
