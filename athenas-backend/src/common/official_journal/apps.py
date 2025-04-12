# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class OfficialJournalConfig(AppConfig):
    name = "common.official_journal"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "common.official_journal.api.journal",
        "common.official_journal.api.officialdiary",
        "common.official_journal.api.document",
        "common.official_journal.api.diaryorder",
        "common.official_journal.api.devolution",
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
    Application = importlib.import_module("default.views").Application

    Application.register_stylesheet(
        "/%(context)s/static/common/official_journal/styles.css"
    )

    js_paths = (
        "/%(context)s/static/common/official_journal/JournalRestful.js",
        "/%(context)s/static/common/official_journal/JournalSuplementRestful.js",
        "/%(context)s/static/common/official_journal/JournalSuplementWindow.js",
        "/%(context)s/static/common/official_journal/JournalSuplementGrid.js",
        "/%(context)s/static/common/official_journal/JournalWindow.js",
        "/%(context)s/static/common/official_journal/JournalGrid.js",
        "/%(context)s/static/common/official_journal/Manage.js",
        "/%(context)s/static/common/official_journal/official_diary/Grid.js",
        "/%(context)s/static/common/official_journal/official_diary/Manage.js",
        "/%(context)s/static/common/official_journal/official_diary/Restful.js",
        "/%(context)s/static/common/official_journal/official_diary/Window.js",
        "/%(context)s/static/common/official_journal/filters/FilterMixin.js",
        "/%(context)s/static/common/official_journal/filters/FilterWindow.js",
        "/%(context)s/static/common/official_journal/filters/OriginDepartament.js",
        "/%(context)s/static/common/official_journal/filters/SendDateWindow.js",
        "/%(context)s/static/common/official_journal/filters/ProtocolWindow.js",
        "/%(context)s/static/common/official_journal/document/Grid.js",
        "/%(context)s/static/common/official_journal/document/Manage.js",
        "/%(context)s/static/common/official_journal/document/Restful.js",
        "/%(context)s/static/common/official_journal/document/Window.js",
        "/%(context)s/static/common/official_journal/document/DiaryWindow.js",
        "/%(context)s/static/common/official_journal/devolution/Grid.js",
        "/%(context)s/static/common/official_journal/devolution/Manage.js",
        "/%(context)s/static/common/official_journal/devolution/Restful.js",
        "/%(context)s/static/common/official_journal/devolution/Window.js",
        "/%(context)s/static/common/official_journal/diaryorder/Grid.js",
        "/%(context)s/static/common/official_journal/diaryorder/Manage.js",
        "/%(context)s/static/common/official_journal/diaryorder/Restful.js",
        "/%(context)s/static/common/official_journal/diaryorder/Window.js",
        "/%(context)s/static/common/official_journal/diaryorder/DepartmentOrganGrid.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="common")
