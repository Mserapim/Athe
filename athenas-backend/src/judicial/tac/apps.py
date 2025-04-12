# -*- coding:utf-8 -*-

import importlib
from django.apps import AppConfig


class TacConfig(AppConfig):
    name = "judicial.tac"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "judicial.tac.api.activityhistory",
        "judicial.tac.api.activity",
        "judicial.tac.api.document",
        "judicial.tac.api.managementtac",
        "judicial.tac.api.responsible",
        "judicial.tac.rpc.tac",
    ]

    def ready(self):

        register_statics()
        connect_signals()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """
    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    # O sinal historico não estava inserido no settings no momento que houve a mudança para o apps.conf.
    # por isso não foi habilitado aqui.
    # importlib.import_module('judicial.tac.signals.historico')

    pass


def register_statics():

    Application = importlib.import_module("default.views").Application

    """Registro dos Javascripts para este aplicativo"""
    js_paths = (
        "/%(context)s/static/judicial/tac/ManagerTAC.js",
        "/%(context)s/static/judicial/tac/ActivityGrid.js",
        "/%(context)s/static/judicial/tac/ActivityRestful.js",
        "/%(context)s/static/judicial/tac/ActivityWindow.js",
        "/%(context)s/static/judicial/tac/ProcessNumberFineWindow.js",
        "/%(context)s/static/judicial/tac/Responsible/ResponsibleGrid.js",
        "/%(context)s/static/judicial/tac/Responsible/ResponsibleRestful.js",
        "/%(context)s/static/judicial/tac/Responsible/ResponsibleWindow.js",
        "/%(context)s/static/judicial/tac/ActivityHistory/ActivityHistoryGrid.js",
        "/%(context)s/static/judicial/tac/ActivityHistory/ActivityHistoryRestful.js",
        "/%(context)s/static/judicial/tac/ActivityHistory/ActivityHistoryWindow.js",
        "/%(context)s/static/judicial/tac/ActivityHistory/ActivityHistoryRestfulWindow.js",
        "/%(context)s/static/judicial/tac/Document/DocumentRestful.js",
        "/%(context)s/static/judicial/tac/Document/DocumentGrid.js",
        "/%(context)s/static/judicial/tac/Document/DocumentWindow.js",
        "/%(context)s/static/judicial/tac/ManagementTAC/ManagementTACRestful.js",
        "/%(context)s/static/judicial/tac/ManagementTAC/ManagementTACWindow.js",
        "/%(context)s/static/judicial/tac/ManagementTAC/WindowSignature.js",
        "/%(context)s/static/judicial/tac/ManagementTAC/ManagementTACGrid.js",
        "/%(context)s/static/judicial/tac/ManagerTAC.js",
        "/%(context)s/static/judicial/tac/FollowDeadlineTAC.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="judicial")
