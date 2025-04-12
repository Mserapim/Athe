# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class ProcessoConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "edocs.processo"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "edocs.processo.api",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        loaders()
        # carregar qualquer outra coisa necessária ao app


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
        "/%(context)s/static/edocs/processo/config/Restful.js",
        "/%(context)s/static/edocs/processo/config/Panel.js",
        "/%(context)s/static/edocs/processo/config/Manager.js",
        "/%(context)s/static/edocs/processo/justificativa/Restful.js",
        "/%(context)s/static/edocs/processo/justificativa/Window.js",
        "/%(context)s/static/edocs/processo/admin/processoAdminRestful.js",
        "/%(context)s/static/edocs/processo/admin/processoAdminWindow.js",
        "/%(context)s/static/edocs/processo/admin/processoAdminGrid.js",
        "/%(context)s/static/edocs/processo/admin/Manager.js",
        "/%(context)s/static/edocs/processo/consulta/processoComumRestful.js",
        "/%(context)s/static/edocs/processo/consulta/processoComumWindow.js",
        "/%(context)s/static/edocs/processo/consulta/processoComumGrid.js",
        "/%(context)s/static/edocs/processo/consulta/Manager.js",
        "/%(context)s/static/edocs/processo/referencia/Restful.js",
        "/%(context)s/static/edocs/processo/referencia/Window.js",
        "/%(context)s/static/edocs/processo/referencia/Grid.js",
        "/%(context)s/static/edocs/movimentacao/Restful.js",
        "/%(context)s/static/edocs/processo/excluirWindow.js",
        "/%(context)s/static/edocs/processo/situacao/Restful.js",
        "/%(context)s/static/edocs/processo/situacao/Window.js",
        "/%(context)s/static/edocs/processo/situacao/Grid.js",
        "/%(context)s/static/edocs/processo/situacao/Manager.js",
        "/%(context)s/static/edocs/processo/assunto/Restful.js",
        "/%(context)s/static/edocs/processo/assunto/Window.js",
        "/%(context)s/static/edocs/processo/assunto/Grid.js",
        "/%(context)s/static/edocs/processo/assunto/Manager.js",
        "/%(context)s/static/edocs/processo/Restful.js",
        "/%(context)s/static/edocs/processo/ImprimirForm.js",
        "/%(context)s/static/edocs/processo/movprocessoWindow.js",
        "/%(context)s/static/edocs/processo/movprocessoGrid.js",
        "/%(context)s/static/edocs/processo/movimentarLoteWindow.js",
        "/%(context)s/static/edocs/processo/movimentarWindow.js",
        "/%(context)s/static/edocs/processo/openWindow.js",
        "/%(context)s/static/edocs/processo/consulta/processDetailsPanel.js",
        "/%(context)s/static/edocs/processo/Window.js",
        "/%(context)s/static/edocs/processo/SaidaGrid.js",
        "/%(context)s/static/edocs/processo/EntradaGrid.js",
        "/%(context)s/static/edocs/processo/Manager.js",
        "/%(context)s/static/edocs/processo/taxonomy/MatterRestful.js",
        "/%(context)s/static/edocs/processo/taxonomy/MatterGrid.js",
        "/%(context)s/static/edocs/processo/taxonomy/MatterWindow.js",
        "/%(context)s/static/edocs/processo/SubjectWindow.js",
        "/%(context)s/static/edocs/processo/ProcessScopeTree.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="edocs")


def loaders():
    importlib.import_module("edocs.processo.loader")
