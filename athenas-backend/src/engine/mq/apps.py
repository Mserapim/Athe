# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class MqConfig(AppConfig):
    name = "engine.mq"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "engine.mq.api.task",
        "engine.mq.api.report",
    ]

    def ready(self):
        register_statics()
        load_notify()
        # connect_signals()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def load_notify():
    importlib.import_module("engine.mq.notify")


def register_statics():
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/engine/notify/Manage.js",
        "/%(context)s/static/engine/mq/TaskRestful.js",
        "/%(context)s/static/engine/mq/TaskWindow.js",
        "/%(context)s/static/engine/mq/TaskGrid.js",
        "/%(context)s/static/engine/mq/TaskManage.js",
        "/%(context)s/static/engine/mq/TaskMessagesRestful.js",
        "/%(context)s/static/engine/mq/TaskMessagesWindow.js",
        "/%(context)s/static/engine/mq/TaskMessagesGrid.js",
        "/%(context)s/static/engine/mq/Report.js",
        "/%(context)s/static/engine/mq/OutputFormatReportMixin.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="engine")
