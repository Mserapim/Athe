# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class AuditoriaConfig(AppConfig):
    name = "auditoria"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "auditoria.views",
        "auditoria.api.linelog",
        "auditoria.api.auditlog",
    ]

    def ready(self):
        register_statics()
        # connect_signals()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/auditoria/LineLogRestful.js",
        "/%(context)s/static/auditoria/LineLogWindow.js",
        "/%(context)s/static/auditoria/LineLogGrid.js",
        "/%(context)s/static/auditoria/LineLogManage.js",
        "/%(context)s/static/auditoria/auditlog/Restful.js",
        "/%(context)s/static/auditoria/auditlog/Window.js",
        "/%(context)s/static/auditoria/auditlog/Grid.js",
        "/%(context)s/static/auditoria/auditlog/Manage.js",
        "/%(context)s/static/auditoria/auditlog/ContentTypeRestful.js",
        "/%(context)s/static/auditoria/auditlog/ContentTypeWindow.js",
        "/%(context)s/static/auditoria/auditlog/ContentTypeGrid.js",
        "/%(context)s/static/auditoria/auditlog/ContentTypeManage.js",
        "/%(context)s/static/auditoria/auditlog/ContentTypeFilterAction.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="core")
