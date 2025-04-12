# -.- coding: utf-8 -.-
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()


from esocial.models import *


def run():
    # print(S1200.objects.get(pk=97098).validation_xml_schema())
    print(S1200.objects.get(pk=97098).generate_xml_with_value())


if __name__ == "__main__":
    run()
