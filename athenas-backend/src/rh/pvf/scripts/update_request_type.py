# -.- coding: utf-8 -.-
import os
import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from rh.pvf.models import PortalRequest


def main():
    pass
    # update_request_type()


if __name__ == "__main__":
    main()
