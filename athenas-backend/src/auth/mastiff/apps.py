# -*- coding:utf-8 -*-

from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "auth.mastiff"
    verbose_name = "Auth Mastiff"

    # controllers = [
    #    'auth.mastiff.views',
    # ]

    # def ready(self):
    #    register_statics()
    #    connect_signals()
    # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():
    # Application = importlib.import_module('default.views').Application

    # Application.register_javascript('/%(context)s/static/auditoria/LineLogRestful.js')
    pass
