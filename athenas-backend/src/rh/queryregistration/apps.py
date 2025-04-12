# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class ConsultationConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.queryregistration"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "rh.queryregistration.api.consultation",
        "rh.queryregistration.api.report",
        "rh.queryregistration.api.tags",
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
        "/%(context)s/static/rh/queryregistration/ConsultationManage.js",
        "/%(context)s/static/rh/queryregistration/ConsultationGrid.js",
        "/%(context)s/static/rh/queryregistration/ConsultationRestful.js",
        "/%(context)s/static/rh/queryregistration/ConsultationWindow.js",
        "/%(context)s/static/rh/queryregistration/TagsWindow.js",
        "/%(context)s/static/rh/queryregistration/tags/Manage.js",
        "/%(context)s/static/rh/queryregistration/tags/Grid.js",
        "/%(context)s/static/rh/queryregistration/tags/Restful.js",
        "/%(context)s/static/rh/queryregistration/tags/Window.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")
