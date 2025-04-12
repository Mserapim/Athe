# -.- coding: utf-8 -.-
import django
import os


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()


from esocial.managers.file_support import csv_to_json, create_django_model_by_json_model


def run():
    csv_to_json(recreate=True, acronyms=["s2200"])
    create_django_model_by_json_model(recreate=True, acronyms=["s2200"])


if __name__ == "__main__":
    run()
