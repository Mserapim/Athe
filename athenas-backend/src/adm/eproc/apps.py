# -*- coding:utf-8 -*-

import importlib

from django.apps import AppConfig


class EprocConfig(AppConfig):
    name = "adm.eproc"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = []

    def ready(self):
        register_statics()


def register_statics():
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/adm/js/core.js",
        "/%(context)s/static/adm/js/eproc.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="adm")
