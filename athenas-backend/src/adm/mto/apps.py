# -*- coding:utf-8 -*-

import importlib

from django.apps import AppConfig


class MtoConfig(AppConfig):
    name = "adm.mto"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "adm.mto.api.expenseelementsubitem",
        "adm.mto.api.expenseelement",
    ]

    def ready(self):
        register_statics()


def register_statics():
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/adm/js/core.js",
        "/%(context)s/static/adm/js/mto.js",
        "/%(context)s/static/adm/mto/expenseelement/Restful.js",
        "/%(context)s/static/adm/mto/expenseelement/Window.js",
        "/%(context)s/static/adm/mto/expenseelement/Grid.js",
        "/%(context)s/static/adm/mto/expenseelement/subitem/Restful.js",
        "/%(context)s/static/adm/mto/expenseelement/subitem/Window.js",
        "/%(context)s/static/adm/mto/expenseelement/subitem/Grid.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="adm")
