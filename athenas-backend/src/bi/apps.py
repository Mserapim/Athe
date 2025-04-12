# -*- coding:utf-8 -*-

import importlib
from django.apps import AppConfig


class BIConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "bi"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = ["bi.views"]

    def ready(self):
        register_statics()


def register_statics():
    Application = importlib.import_module("default.views").Application

    Application.register_javascript("/%(context)s/static/bi/js/regions.js", scope="bi")
