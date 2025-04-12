# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class SCMMPConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.scmmp"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "rh.scmmp.api.processojudicial",
        "rh.scmmp.api.membroprocesso",
        "rh.scmmp.api.faserecursal",
        "rh.scmmp.api.sancaojudicial",
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

    Application.register_stylesheet("/%(context)s/static/rh/scmmp/scmmp.css")

    js_paths = (
        "/%(context)s/static/rh/scmmp/processojudicial/ProcessoJudicialRestful.js",
        "/%(context)s/static/rh/scmmp/processojudicial/ProcessoJudicialWindow.js",
        "/%(context)s/static/rh/scmmp/processojudicial/ProcessoJudicialGrid.js",
        # '/%(context)s/static/rh/scmmp/processojudicial/Manage.js',
        "/%(context)s/static/rh/scmmp/membroprocesso/MembroProcessoRestful.js",
        "/%(context)s/static/rh/scmmp/membroprocesso/MembroProcessoWindow.js",
        "/%(context)s/static/rh/scmmp/membroprocesso/MembroProcessoGrid.js",
        "/%(context)s/static/rh/scmmp/faserecursal/FaseRecursalRestful.js",
        "/%(context)s/static/rh/scmmp/faserecursal/FaseRecursalWindow.js",
        "/%(context)s/static/rh/scmmp/faserecursal/FaseRecursalGrid.js",
        "/%(context)s/static/rh/scmmp/sancaojudicial/SancaoJudicialRestful.js",
        "/%(context)s/static/rh/scmmp/sancaojudicial/SancaoJudicialWindow.js",
        "/%(context)s/static/rh/scmmp/sancaojudicial/SancaoJudicialGrid.js",
        "/%(context)s/static/rh/scmmp/Manage.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")


def loaders():
    pass
