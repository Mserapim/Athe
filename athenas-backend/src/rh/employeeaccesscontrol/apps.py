# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class EAControlConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.employeeaccesscontrol"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "rh.employeeaccesscontrol.api.employee",
        "rh.employeeaccesscontrol.api.authemployee",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        loaders()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    # importlib.import_module('rh.employeeaccesscontrol.signals.teste')
    pass


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui."""

    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/rh/employeeaccesscontrol/employee/Restful.js",
        "/%(context)s/static/rh/employeeaccesscontrol/employee/Window.js",
        "/%(context)s/static/rh/employeeaccesscontrol/employee/Grid.js",
        "/%(context)s/static/rh/employeeaccesscontrol/employee/Manage.js",
        "/%(context)s/static/rh/employeeaccesscontrol/authemployee/Restful.js",
        "/%(context)s/static/rh/employeeaccesscontrol/authemployee/Window.js",
        "/%(context)s/static/rh/employeeaccesscontrol/authemployee/Grid.js",
        "/%(context)s/static/rh/employeeaccesscontrol/authemployee/Manage.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")


def loaders():
    pass
