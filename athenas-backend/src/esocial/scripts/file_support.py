# -.- coding: utf-8 -.-
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.middleware import set_current_user
from esocial.managers.file_support import get_register_model


set_current_user("gustavodettenborn")


def _read_model_static_fields(acronym):
    _model = get_register_model(acronym)
    return {
        acronym: {
            "XML_SCHEMA_NAME": getattr(_model, "XML_SCHEMA_NAME", ""),
            "NAME": getattr(_model, "NAME", ""),
            "XMLNS": getattr(_model, "XMLNS", ""),
            "GROUP": getattr(_model, "GROUP", "1"),
            "ACTION_PERM": getattr(_model, "ACTION_PERM", "ACTION"),
        }
    }


def run():
    print(_read_model_static_fields("s1010"))


if __name__ == "__main__":
    run()
