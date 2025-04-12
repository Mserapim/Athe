# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class PontoConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.ponto"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # PONTO
        "rh.ponto.api.falta",
        "rh.ponto.api.reports",
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
        "/%(context)s/static/rh/falta/FaltaRestful.js",
        "/%(context)s/static/rh/falta/FaltaWindow.js",
        "/%(context)s/static/rh/falta/FaltaGrid.js",
        "/%(context)s/static/rh/falta/AnotacaoWindow.js",
        "/%(context)s/static/rh/falta/RelatorioWindow.js",
        "/%(context)s/static/rh/falta/Manage.js",
        "/%(context)s/static/rh/falta/employee/Manage.js",
        "/%(context)s/static/rh/falta/employee/Restful.js",
        "/%(context)s/static/rh/falta/employee/Grid.js",
        "/%(context)s/static/rh/falta/employee/Window.js",
        "/%(context)s/static/rh/falta/employee/ProcessaFaltaWindow.js",
        "/%(context)s/static/rh/falta/remocao_falta/Manage.js",
        "/%(context)s/static/rh/falta/remocao_falta/Restful.js",
        "/%(context)s/static/rh/falta/remocao_falta/Grid.js",
        "/%(context)s/static/rh/falta/remocao_falta/Window.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")


def loaders():
    pass
