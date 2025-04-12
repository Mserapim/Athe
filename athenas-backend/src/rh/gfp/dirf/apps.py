# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class GFPDirfConfig(
    AppConfig
):  # Substituir "Sample" pelo nome que preferir dar ao AppConfig
    name = "rh.gfp.dirf"  # Caminho completo para o app. Ex: rh.gfp.dirf
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        # Aqui devem ser listados os caminhos dos controllers do app. Ex: web.api.cms.metadata
        "rh.gfp.dirf.api.dirf",
    ]

    def ready(self):
        """
        O carregamento de partes necessárias ao app.
        """
        register_statics()
        connect_signals()
        # carregar qualquer outra coisa necessária ao app
        loaders()


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
        "/%(context)s/static/rh/js/dirf.js",
        "/%(context)s/static/rh/gfp/dirf/DialectWindow.js",
        "/%(context)s/static/rh/gfp/dirf/DialectGrid.js",
        "/%(context)s/static/rh/gfp/dirf/DialectRestful.js",
        "/%(context)s/static/rh/gfp/dirf/DialectManage.js",
        "/%(context)s/static/rh/gfp/dirf/DeclaracaoWindow.js",
        "/%(context)s/static/rh/gfp/dirf/DeclaracaoGrid.js",
        "/%(context)s/static/rh/gfp/dirf/DeclaracaoRestful.js",
        "/%(context)s/static/rh/gfp/dirf/DeclaracaoManage.js",
        "/%(context)s/static/rh/gfp/dirf/TokenWindow.js",
        "/%(context)s/static/rh/gfp/dirf/TokenGrid.js",
        "/%(context)s/static/rh/gfp/dirf/TokenRestful.js",
        "/%(context)s/static/rh/gfp/dirf/NaturezaRendimentoWindow.js",
        "/%(context)s/static/rh/gfp/dirf/NaturezaRendimentoGrid.js",
        "/%(context)s/static/rh/gfp/dirf/NaturezaRendimentoRestful.js",
        "/%(context)s/static/rh/gfp/dirf/DirfSummaryWindow.js",
        "/%(context)s/static/rh/gfp/dirf/DirfSummaryGrid.js",
        "/%(context)s/static/rh/gfp/dirf/DirfSummaryRestful.js",
        "/%(context)s/static/rh/gfp/dirf/DirfSummaryManage.js",
        "/%(context)s/static/rh/gfp/dirf/DemonstrativoWindow.js",
        "/%(context)s/static/rh/gfp/dirf/DemonstrativoGrid.js",
        "/%(context)s/static/rh/gfp/dirf/DemonstrativoRestful.js",
        "/%(context)s/static/rh/gfp/dirf/DemonstrativoManage.js",
    )

    for path in js_paths:
        Application.register_javascript(path, scope="rh")


def loaders():
    pass
