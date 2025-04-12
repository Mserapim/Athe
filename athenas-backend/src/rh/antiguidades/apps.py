# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class AntiguidadesConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.antiguidades"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "rh.antiguidades.api.lista_antiguidades_membros",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        # connect_signals()
        # loaders()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    # importlib.import_module('rh.gratifications_manager.signals')
    pass


def loaders():
    pass


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application = importlib.import_module('default.views').Application
        '/%(context)s/static/web/js/shortcuts.js',

        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """

    Application = importlib.import_module("default.views").Application

    js_paths = (
        # ORGANIZED LOADERS ----------------------------------------------------------------------------
        "/%(context)s/static/rh/lista_antiguidade_membros/Manage.js",
        "/%(context)s/static/rh/lista_antiguidade_membros/Grid.js",
        "/%(context)s/static/rh/lista_antiguidade_membros/Restful.js",
        "/%(context)s/static/rh/lista_antiguidade_membros/Window.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")

    # 'Registro dos Stylesheet's para este aplicativo'
    Application.register_stylesheet("/%(context)s/static/rh/images/fopag/fopag.css")
    Application.register_stylesheet("/%(context)s/static/rh/images/fopag/style.css")
    Application.register_stylesheet(
        "/%(context)s/static/rh/images/progressoes/sprite-progressoes.css"
    )
