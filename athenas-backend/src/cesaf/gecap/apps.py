# -*- coding:utf-8 -*-

import importlib
from django.apps import AppConfig


class GecapConfig(AppConfig):
    name = "cesaf.gecap"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "cesaf.gecap.views",
        "cesaf.gecap.reports",
        "cesaf.gecap.api.areaconhecimento",
    ]

    def ready(self):
        register_statics()


def register_statics():
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/cesaf/js/core.js",
        "/%(context)s/static/cesaf/js/gecap.js",
        "/%(context)s/static/cesaf/js/concurso.js",
        "/%(context)s/static/cesaf/gecap/areaconhecimento/AreaConhecimentoGrid.js",
        "/%(context)s/static/cesaf/gecap/areaconhecimento/AreaConhecimentoRestful.js",
        "/%(context)s/static/cesaf/gecap/areaconhecimento/AreaConhecimentoWindow.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="cesaf")
