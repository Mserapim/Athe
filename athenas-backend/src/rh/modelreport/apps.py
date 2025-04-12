# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class ModelReportConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.modelreport"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "rh.modelreport.api.modelpdf",
        "rh.modelreport.api.modelodt",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:


        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/rh/modelreport/pdf/Manage.js",
        "/%(context)s/static/rh/modelreport/pdf/Grid.js",
        "/%(context)s/static/rh/modelreport/pdf/Restful.js",
        "/%(context)s/static/rh/modelreport/pdf/Window.js",
        "/%(context)s/static/rh/modelreport/pdf/ReportWindow.js",
        "/%(context)s/static/rh/modelreport/odt/Manage.js",
        "/%(context)s/static/rh/modelreport/odt/Grid.js",
        "/%(context)s/static/rh/modelreport/odt/Restful.js",
        "/%(context)s/static/rh/modelreport/odt/Window.js",
        "/%(context)s/static/rh/modelreport/odt/ReportWindow.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")
