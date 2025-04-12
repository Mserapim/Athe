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
    name = "common.internal_security"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "common.internal_security.api.emotionalstate",
        "common.internal_security.api.person",
        "common.internal_security.api.incidentreport",
    ]

    def ready(self):
        register_statics()
        connect_signals()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    importlib.import_module("common.internal_security.signals.incident")


def register_statics():
    Application = importlib.import_module("default.views").Application

    Application.register_stylesheet(
        "/%(context)s/static/common/internalSecurity/theme.css"
    )
    Application.register_stylesheet(
        "/%(context)s/static/common/internalSecurity/isec.css"
    )

    js_paths = (
        "/%(context)s/static/common/internalSecurity/emotionalstate/Restful.js",
        "/%(context)s/static/common/internalSecurity/emotionalstate/Window.js",
        "/%(context)s/static/common/internalSecurity/emotionalstate/Grid.js",
        "/%(context)s/static/common/internalSecurity/person/Restful.js",
        "/%(context)s/static/common/internalSecurity/person/Window.js",
        "/%(context)s/static/common/internalSecurity/person/Grid.js",
        "/%(context)s/static/common/internalSecurity/incidentReport/Restful.js",
        "/%(context)s/static/common/internalSecurity/incidentReport/Window.js",
        "/%(context)s/static/common/internalSecurity/incidentReport/Grid.js",
        "/%(context)s/static/common/internalSecurity/incidentReport/ViewPanel.js",
        "/%(context)s/static/common/internalSecurity/incidentReport/Manage.js",
        "/%(context)s/static/common/internalSecurity/incidentReport/Widget.js",
        "/%(context)s/static/common/internalSecurity/incidentReport/FilterBaseWindow.js",
        "/%(context)s/static/common/internalSecurity/incidentReport/FilterLocationWindow.js",
        "/%(context)s/static/common/internalSecurity/incidentReport/FilterPersonWindow.js",
        "/%(context)s/static/common/internalSecurity/incidentReport/FilterPeriodWindow.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="common")
