# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib

from django.apps import AppConfig


class CadastramentoConfig(AppConfig):
    name = "nomeacao.cadastramento"  # Caminho completo para o app. Ex: nomeacao.cadastramento
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "nomeacao.cadastramento.api.convite_nomeacao",
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
    pass


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:


        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """
    Application = importlib.import_module("default.views").Application

    js_paths = (
        # '/%(context)s/static/appointment/personregistration/constants.js',
        "/%(context)s/static/nomeacao/cadastramento/Restful.js",
        "/%(context)s/static/nomeacao/cadastramento/Window.js",
        "/%(context)s/static/nomeacao/cadastramento/Grid.js",
        "/%(context)s/static/nomeacao/cadastramento/Manage.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="nomeacao")


def loaders():
    signals_module_enabled = (
        # 'rh.signals.resignation_move',
    )

    for signal_module in signals_module_enabled:
        importlib.import_module(signal_module)
