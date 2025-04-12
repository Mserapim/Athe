# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

# import importlib
from django.apps import AppConfig


class NotificationConfig(AppConfig):
    name = "engine.notification"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "engine.notification.views",
    ]

    # def ready(self):
    #     register_statics()
    #     connect_signals()
    #     carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():
    # Application = importlib.import_module('default.views').Application

    # Application.register_javascript('/%(context)s/static/engine/js/core.js')
    pass
