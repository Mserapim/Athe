# -*- coding:utf-8 -*-

import importlib
from django.apps import AppConfig


class CNMPConfig(AppConfig):
    name = "corregedoria.cnmp"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = ["corregedoria.cnmp.api.cnmp", "corregedoria.cnmp.api.communication"]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        # carregar qualquer outra coisa necessária ao app
        load_notify()


def load_notify():
    # importlib.import_module('corregedoria.notify')
    importlib.import_module("corregedoria.cnmp.notify")


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    importlib.import_module("corregedoria.cnmp.signals.autocreatecommunication")


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application = importlib.import_module('default.views').Application

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """

    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/corregedoria/cnmp/Manage.js",
        "/%(context)s/static/corregedoria/cnmp/Grid.js",
        "/%(context)s/static/corregedoria/cnmp/Window.js",
        "/%(context)s/static/corregedoria/cnmp/Restful.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="corregedoria")
