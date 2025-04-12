"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib

from django.apps import AppConfig


class HealthConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "health"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "health.api.diagnosisprocedure",
        "health.api.exam",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        loaders()
        # carregar qualquer outra coisa necessária ao app


def loaders():
    pass


def connect_signals():
    pass


def register_statics():
    """O registro dos arquivos estáticos do app deve ser feito aqui.

    Ex:

        Application = importlib.import_module('default.views').Application

        Application.register_javascript('/%(context)s/static/web/js/shortcuts.js')
        Application.register_stylesheet('/%(context)s/static/web/css/styles.css')
    """
    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/health/DiagnosisProcedureGrid.js",
        "/%(context)s/static/health/DiagnosisProcedureRestful.js",
        "/%(context)s/static/health/DiagnosisProcedureWindow.js",
        "/%(context)s/static/health/DiagnosisProcedureManage.js",
        "/%(context)s/static/health/ExamGrid.js",
        "/%(context)s/static/health/ExamRestful.js",
        "/%(context)s/static/health/ExamWindow.js",
        "/%(context)s/static/health/ExamManage.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="health")
