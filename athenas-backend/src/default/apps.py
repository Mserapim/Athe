# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class DefaultConfig(AppConfig):
    # default_auto_field = 'django.db.models.BigAutoField'
    name = "default"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "default.views",
        "default.api.debug",
        "default.api.stats",
    ]

    def ready(self):
        register_statics()
        importlib.import_module("default.sysinfo")


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():
    # Application = importlib.import_module('default.views').Application

    # Application.register_javascript('/%(context)s/static/engine/notify/Manage.js')
    pass
