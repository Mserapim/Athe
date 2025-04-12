# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class PensaoConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.pensao"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "rh.pensao.views",
        "rh.pensao.api.employee_pension",
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
    pass


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application = importlib.import_module('default.views').Application

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """

    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/rh/js/pensao.js",
        "/%(context)s/static/rh/pension/PensionerRestful.js",
        "/%(context)s/static/rh/pension/PensionerGrid.js",
        "/%(context)s/static/rh/pension/PensionerManager.js",
        #'/%(context)s/static/rh/pension/PensionerWindow.js',
        "/%(context)s/static/rh/pension/Restful.js",
        "/%(context)s/static/rh/pension/Grid.js",
        "/%(context)s/static/rh/pension/Manager.js",
        "/%(context)s/static/rh/pension/Window.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")


def loaders():
    importlib.import_module("rh.pensao.signals.pensao")
    importlib.import_module("rh.pensao.signals.gfp")
