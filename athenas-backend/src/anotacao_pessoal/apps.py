# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class AnotacaoPessoalConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "anotacao_pessoal"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        #'rh.gratifications_manager.api.cumulative_exercises',
        "anotacao_pessoal.api.anotacaopessoal",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        # carregar qualquer outra coisa necessária ao app


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
        #'/%(context)s/static/anotacao/Manage.js',
        #'/%(context)s/static/anotacao/Grid.js',
        #'/%(context)s/static/anotacao/Restful.js',
        #'/%(context)s/static/anotacao/Window.js',
        "/%(context)s/static/anotacao_pessoal/anotacao/Manage.js",
        "/%(context)s/static/anotacao_pessoal/anotacao/anotacao_pessoal/Manage.js",
        "/%(context)s/static/anotacao_pessoal/anotacao/anotacao_pessoal/Grid.js",
        "/%(context)s/static/anotacao_pessoal/anotacao/anotacao_pessoal/Restful.js",
        "/%(context)s/static/anotacao_pessoal/anotacao/anotacao_pessoal/Window.js",
        "/%(context)s/static/anotacao_pessoal/anotacao/servidor/Manage.js",
        "/%(context)s/static/anotacao_pessoal/anotacao/servidor/Grid.js",
        "/%(context)s/static/anotacao_pessoal/anotacao/servidor/Restful.js",
        "/%(context)s/static/anotacao_pessoal/anotacao/servidor/Window.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="anotacao_pessoal")

    # 'Registro dos Stylesheet's para este aplicativo'
    # Application.register_stylesheet('/%(context)s/static/rh/images/fopag/fopag.css')
    # Application.register_stylesheet('/%(context)s/static/rh/images/fopag/style.css')
    # Application.register_stylesheet('/%(context)s/static/rh/images/progressoes/sprite-progressoes.css')
