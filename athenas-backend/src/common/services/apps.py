# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django import apps


class AppConfig(apps.AppConfig):
    name = "common.services"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "common.services.api.services",
    ]

    def ready(self):
        register_statics()


def register_statics():
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/common/services/scheduled_services/Restful.js",
        "/%(context)s/static/common/services/scheduled_services/Manage.js",
        "/%(context)s/static/common/services/scheduled_services/Window.js",
        "/%(context)s/static/common/services/scheduled_services/Grid.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="common")
