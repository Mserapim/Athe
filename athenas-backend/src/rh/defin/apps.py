# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django import apps


class DEFINConfig(apps.AppConfig):
    name = "rh.defin"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "rh.defin.api.eventual_provider",
        "rh.defin.api.entry",
        "rh.defin.api.workplace",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui."""

    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/rh/defin/eventual_provider/pf/Restful.js",
        "/%(context)s/static/rh/defin/eventual_provider/pf/Manage.js",
        "/%(context)s/static/rh/defin/eventual_provider/pf/Window.js",
        "/%(context)s/static/rh/defin/eventual_provider/pf/Grid.js",
        "/%(context)s/static/rh/defin/entry/pf_provider/Restful.js",
        "/%(context)s/static/rh/defin/entry/pf_provider/Manage.js",
        "/%(context)s/static/rh/defin/entry/pf_provider/Window.js",
        "/%(context)s/static/rh/defin/entry/pf_provider/Grid.js",
        "/%(context)s/static/rh/defin/reports/ProviderEntryReport.js",
        "/%(context)s/static/rh/defin/workplace/Restful.js",
        "/%(context)s/static/rh/defin/workplace/Manage.js",
        "/%(context)s/static/rh/defin/workplace/Grid.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")
