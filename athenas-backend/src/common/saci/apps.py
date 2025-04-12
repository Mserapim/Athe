# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class SACIConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "common.saci"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "common.saci.api.attendance",
        "common.saci.api.typology",
        "common.saci.api.configuration",
        "common.saci.api.report",
        "common.saci.api.attachment",
        "common.saci.api.workplace",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        sync()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    importlib.import_module("common.saci.signals.custom")


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application = importlib.import_module('default.views').Application

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """
    # pass
    Application = importlib.import_module("default.views").Application

    Application.register_stylesheet("/%(context)s/static/common/saci/saci.css")

    js_paths = (
        "/%(context)s/static/common/saci/Configuration.js",
        "/%(context)s/static/common/saci/ReportManage.js",
        "/%(context)s/static/common/saci/queue/PersonWindow.js",
        "/%(context)s/static/common/saci/queue/PersonRestful.js",
        "/%(context)s/static/common/saci/queue/PersonGrid.js",
        "/%(context)s/static/common/saci/attendance/Restful.js",
        "/%(context)s/static/common/saci/attendance/Window.js",
        "/%(context)s/static/common/saci/attendance/Grid.js",
        "/%(context)s/static/common/saci/attendance/HistoricStepWindow.js",
        "/%(context)s/static/common/saci/clerk/Restful.js",
        "/%(context)s/static/common/saci/clerk/Window.js",
        "/%(context)s/static/common/saci/clerk/Grid.js",
        "/%(context)s/static/common/saci/clerk/Manage.js",
        "/%(context)s/static/common/saci/attendance/ForwardExternalWindow.js",
        "/%(context)s/static/common/saci/attendance/ForwardWindow.js",
        "/%(context)s/static/common/saci/attendance/FinalizeWindow.js",
        "/%(context)s/static/common/saci/prosecutor/Restful.js",
        "/%(context)s/static/common/saci/prosecutor/Window.js",
        "/%(context)s/static/common/saci/prosecutor/Grid.js",
        "/%(context)s/static/common/saci/prosecutor/Manage.js",
        "/%(context)s/static/common/saci/prosecutor/ForwardInternalWindow.js",
        "/%(context)s/static/common/saci/prosecutor/ForwardExternalWindow.js",
        "/%(context)s/static/common/saci/prosecutor/FinalizeWindow.js",
        "/%(context)s/static/common/saci/typology/Restful.js",
        "/%(context)s/static/common/saci/typology/Window.js",
        "/%(context)s/static/common/saci/typology/Grid.js",
        "/%(context)s/static/common/saci/typology/Manage.js",
        "/%(context)s/static/common/saci/step/Restful.js",
        "/%(context)s/static/common/saci/step/Window.js",
        "/%(context)s/static/common/saci/step/Grid.js",
        "/%(context)s/static/common/saci/attachment/Restful.js",
        "/%(context)s/static/common/saci/attachment/Window.js",
        "/%(context)s/static/common/saci/attachment/Grid.js",
        "/%(context)s/static/common/saci/params/WorkplaceRestful.js",
        "/%(context)s/static/common/saci/params/WorkplaceWindow.js",
        "/%(context)s/static/common/saci/params/WorkplaceGrid.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="common")


def sync():
    importlib.import_module("common.saci.dasync")
