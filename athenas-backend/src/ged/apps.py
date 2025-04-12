# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class GedConfig(AppConfig):
    name = "ged"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "ged.views",
        "ged.api.arquivo",
    ]

    def ready(self):
        register_statics()
        # connect_signals()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():
    # TODO: Avaliar alteração no regiter quando existirem outras dependencias
    Application = importlib.import_module("default.views").Application

    dependecies_workplace_rh = (
        "/%(context)s/static/rh/workplace/Restful.js",
        "/%(context)s/static/rh/workplace/Window.js",
        "/%(context)s/static/rh/workplace/Grid.js",
    )

    js_paths = {
        "/%(context)s/static/ged/arquivo/ArquivoRestful.js": dependecies_workplace_rh,
        "/%(context)s/static/ged/arquivo/ArquivoWindow.js": dependecies_workplace_rh,
        "/%(context)s/static/ged/arquivo/ArquivoGrid.js": dependecies_workplace_rh,
        "/%(context)s/static/ged/arquivo/ArquivoManage.js": dependecies_workplace_rh,
    }

    for path in js_paths:
        Application.register_javascript(path, dependencies=js_paths[path], scope="core")
