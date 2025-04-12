# -*- coding: utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django import apps


class AppConfig(
    apps.AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "common.document_access"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "common.document_access.api.allowed_list_item",
        "common.document_access.api.control",
        "common.document_access.api.control_type",
        "common.document_access.api.document_type",
        "common.document_access.api.legalprerogative",
        "common.document_access.api.log",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        load_subcommands()
        # carregar qualquer outra coisa necessária ao app


def load_subcommands():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    importlib.import_module("common.document_access.management.subcommands.dasync")
    importlib.import_module(
        "common.document_access.management.subcommands.auto_declassify"
    )


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    importlib.import_module("common.document_access.signals.edocs")
    importlib.import_module("common.document_access.signals.siacmp")
    importlib.import_module("common.document_access.signals.daily")


def register_statics():
    Application = importlib.import_module("default.views").Application

    Application.register_stylesheet(
        "/%(context)s/static/common/document_access/style.css"
    )
    Application.register_stylesheet(
        "/%(context)s/static/common/document_access/images/document_access.css"
    )

    js_paths = (
        "/%(context)s/static/common/document_access/documenttype/Grid.js",
        "/%(context)s/static/common/document_access/documenttype/Manage.js",
        "/%(context)s/static/common/document_access/documenttype/Restful.js",
        "/%(context)s/static/common/document_access/documenttype/Window.js",
        "/%(context)s/static/common/document_access/controltype/Grid.js",
        "/%(context)s/static/common/document_access/controltype/Manage.js",
        "/%(context)s/static/common/document_access/controltype/Restful.js",
        "/%(context)s/static/common/document_access/controltype/Window.js",
        "/%(context)s/static/common/document_access/controltype/byUser/Grid.js",
        "/%(context)s/static/common/document_access/controltype/byUser/Restful.js",
        "/%(context)s/static/common/document_access/controltype/byUser/Window.js",
        "/%(context)s/static/common/document_access/control/Grid.js",
        "/%(context)s/static/common/document_access/control/Restful.js",
        "/%(context)s/static/common/document_access/control/Manage.js",
        "/%(context)s/static/common/document_access/control/Window.js",
        "/%(context)s/static/common/document_access/control/changes/BaseJustification.js",
        "/%(context)s/static/common/document_access/control/changes/DeadlineChange.js",
        "/%(context)s/static/common/document_access/control/changes/Declassify.js",
        "/%(context)s/static/common/document_access/control/changes/Reclassify.js",
        "/%(context)s/static/common/document_access/control/filters/BaseWindow.js",
        "/%(context)s/static/common/document_access/control/filters/CtrlTypeWindow.js",
        "/%(context)s/static/common/document_access/control/filters/DocTypeWindow.js",
        "/%(context)s/static/common/document_access/control/filters/SourceWindow.js",
        "/%(context)s/static/common/document_access/protocolcontrol/Grid.js",
        "/%(context)s/static/common/document_access/protocolcontrol/Restful.js",
        "/%(context)s/static/common/document_access/protocolcontrol/Window.js",
        "/%(context)s/static/common/document_access/log/Grid.js",
        "/%(context)s/static/common/document_access/log/Manage.js",
        "/%(context)s/static/common/document_access/log/Modal.js",
        "/%(context)s/static/common/document_access/log/Restful.js",
        "/%(context)s/static/common/document_access/log/Window.js",
        "/%(context)s/static/common/document_access/allowedlistitem/Grid.js",
        "/%(context)s/static/common/document_access/allowedlistitem/Manage.js",
        "/%(context)s/static/common/document_access/allowedlistitem/Modal.js",
        "/%(context)s/static/common/document_access/allowedlistitem/Restful.js",
        "/%(context)s/static/common/document_access/allowedlistitem/Window.js",
        "/%(context)s/static/common/document_access/legalprerogative/Grid.js",
        "/%(context)s/static/common/document_access/legalprerogative/Manage.js",
        "/%(context)s/static/common/document_access/legalprerogative/Restful.js",
        "/%(context)s/static/common/document_access/legalprerogative/Window.js",
        "/%(context)s/static/common/document_access/JustificationWindow.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="common")
