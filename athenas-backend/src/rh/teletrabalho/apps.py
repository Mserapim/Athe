# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class TeletrabalhoConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.teletrabalho"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "rh.teletrabalho.api.teletrabalho_competencia",
        "rh.teletrabalho.api.config_periodo_envio_analisado",
        "rh.teletrabalho.api.gestor_relatorio_semestral",
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
        #'/%(context)s/static/rh/teletrabalho/teletrabalho_competencia/Manage.js',
        #'/%(context)s/static/rh/teletrabalho/teletrabalho_competencia/Grid.js',
        #'/%(context)s/static/rh/teletrabalho/teletrabalho_competencia/Restful.js',
        #'/%(context)s/static/rh/teletrabalho/teletrabalho_competencia/Window.js',
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")

    # 'Registro dos Stylesheet's para este aplicativo'
    Application.register_stylesheet("/%(context)s/static/rh/images/fopag/fopag.css")
    Application.register_stylesheet("/%(context)s/static/rh/images/fopag/style.css")
    Application.register_stylesheet(
        "/%(context)s/static/rh/images/progressoes/sprite-progressoes.css"
    )
